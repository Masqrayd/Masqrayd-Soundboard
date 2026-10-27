#include <obs-module.h>
#include <obs-frontend-api.h>
#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QPushButton>
#include <QLabel>
#include <QTabWidget>
#include <QScrollArea>
#include <QFileDialog>
#include <QInputDialog>
#include <QColorDialog>
#include <QMenu>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QStandardPaths>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QMessageBox>
#include <QSlider>
#include <QTimer>
#include <QUrl>
#include <QColor>
#include <QHash>
#include <QLineEdit>
#include <QSaveFile>
#include <QFileDialog>
#include <QUuid>
#include <QPointer>
#include <vector>
#include <memory>

OBS_DECLARE_MODULE()
OBS_MODULE_USE_DEFAULT_LOCALE("masqrayd-soundboard", "en-US")
MODULE_EXPORT const char *obs_module_description(void) { return "Masqrayd Soundboard: native dock prototype"; }

namespace {
struct Sound {
  QString id, label, path, color = "#9F3655", status = "active";
  double volume = 1.0;
};
class Soundboard : public QWidget {
  QJsonArray sounds;
  QTabWidget *tabs = nullptr;
  QSlider *master = nullptr;
  QMediaPlayer *player = nullptr;
  QAudioOutput *audio = nullptr;
  QString playingId;
  QString libraryRoot;
  QString manifest;
  QHash<QString,QPushButton*> buttons;
  int masterLevel = 80;
public:
  Soundboard() {
    setObjectName("MasqraydSoundboardPanel");
    setMinimumWidth(250);
    setStyleSheet("QWidget#MasqraydSoundboardPanel{background:#22242B;color:#F6EAF0;} QPushButton{padding:7px;border-radius:5px;color:white;} QTabWidget::pane{border:0;}");
    libraryRoot = QDir(QStandardPaths::writableLocation(QStandardPaths::MusicLocation)).filePath("Masqrayd Soundboard");
    QDir().mkpath(libraryRoot);
    manifest = QDir(libraryRoot).filePath("soundboard-library.json");
    audio = new QAudioOutput(this);
    player = new QMediaPlayer(this);
    player->setAudioOutput(audio);
    connect(player, &QMediaPlayer::playbackStateChanged, this, [this](QMediaPlayer::PlaybackState state) {
      if(state == QMediaPlayer::StoppedState) { playingId.clear(); updateLights(); }
    });
    auto *layout = new QVBoxLayout(this);
    auto *header = new QHBoxLayout();
    auto *title = new QLabel("MASQRAYD SOUNDBOARD");
    header->addWidget(title);
    auto *add = new QPushButton("+ Add");
    auto *manage = new QPushButton("Manage");
    header->addWidget(add); header->addWidget(manage);
    layout->addLayout(header);
    tabs = new QTabWidget();
    layout->addWidget(tabs);
    auto *bottom = new QHBoxLayout();
    auto *stop = new QPushButton("Stop All");
    bottom->addWidget(stop);
    bottom->addWidget(new QLabel("Volume"));
    master = new QSlider(Qt::Horizontal);
    master->setRange(0,100); master->setValue(masterLevel);
    bottom->addWidget(master);
    layout->addLayout(bottom);
    connect(stop,&QPushButton::clicked,this,[this](){player->stop();playingId.clear();updateLights();});
    connect(master,&QSlider::valueChanged,this,[this](int v){masterLevel=v;save();updateVolume();});
    connect(add,&QPushButton::clicked,this,[this](){importSounds();});
    connect(manage,&QPushButton::clicked,this,[this](){manageLibrary();});
    load(); refresh();
  }
  void updateVolume() {
    double soundVolume=1.0;
    for(const auto &v:sounds) {auto s=v.toObject();if(s.value("id").toString()==playingId) soundVolume=s.value("volume").toDouble(1.0);}
    audio->setVolume((masterLevel/100.0)*soundVolume);
  }
  void load() {
    QFile f(manifest); if(!f.open(QIODevice::ReadOnly)) return;
    auto doc=QJsonDocument::fromJson(f.readAll());
    auto root=doc.object();
    sounds=root.value("sounds").toArray();
    masterLevel=root.value("masterVolume").toInt(80);
    master->setValue(masterLevel);
  }
  void save() {
    QJsonObject root; root.insert("schema",1);root.insert("masterVolume",masterLevel);root.insert("sounds",sounds);
    QSaveFile f(manifest); if(f.open(QIODevice::WriteOnly)) { f.write(QJsonDocument(root).toJson(QJsonDocument::Indented)); f.commit(); }
  }
  void updateLights() {
    for(auto it=buttons.begin();it!=buttons.end();++it) {
      QString color="#9F3655";
      for(const auto &v:sounds){auto s=v.toObject();if(s.value("id").toString()==it.key())color=s.value("color").toString(color);}
      const bool active=(it.key()==playingId);
      it.value()->setStyleSheet(QString("QPushButton{background:%1;border:%2 solid %3;font-weight:600;}").arg(color).arg(active?3:1).arg(active?"#FFFFFF":"#777777"));
      it.value()->setText(it.value()->property("label").toString()+(active?"  ●":""));
    }
  }
  void refresh() {
    while(tabs->count()) { QWidget *w=tabs->widget(0); tabs->removeTab(0); delete w; } buttons.clear();
    auto *page=new QWidget();
    auto *grid=new QGridLayout(page);
    int idx=0;
    for(const auto &v:sounds) {
      auto s=v.toObject(); if(s.value("status").toString("active")!="active")continue;
      QString id=s.value("id").toString();
      auto *b=new QPushButton(s.value("label").toString());
      b->setProperty("label",s.value("label").toString());
      b->setMinimumHeight(56);
      b->setContextMenuPolicy(Qt::CustomContextMenu);
      connect(b,&QPushButton::clicked,this,[this,id](){play(id);});
      connect(b,&QPushButton::customContextMenuRequested,this,[this,id,b](const QPoint &p){editMenu(id,b->mapToGlobal(p));});
      grid->addWidget(b,idx/3,idx%3);
      buttons.insert(id,b); ++idx;
    }
    grid->setRowStretch(idx/3+1,1);
    auto *scroll=new QScrollArea();
    scroll->setWidgetResizable(true); scroll->setWidget(page);
    tabs->addTab(scroll,"Active");
    updateLights();
  }
  void play(const QString &id) {
    for(const auto &v:sounds) {
      auto s=v.toObject();if(s.value("id").toString()!=id)continue;
      QString path=s.value("path").toString();
      if(!QFileInfo::exists(path)){QMessageBox::warning(this,"Missing sound","File not found: "+path);return;}
      player->stop();playingId=id;
      player->setSource(QUrl::fromLocalFile(path));updateVolume();player->play();updateLights();
      break;
    }
  }
  void importSounds() {
    auto paths=QFileDialog::getOpenFileNames(this,"Add sound effects",libraryRoot,"Audio files (*.wav *.mp3 *.ogg *.flac *.m4a)");
    for(const auto &source:paths) {
      QFileInfo info(source);
      QString id=QUuid::createUuid().toString(QUuid::WithoutBraces);
      QString dest=QDir(libraryRoot).filePath(id+"."+info.suffix().toLower());
      if(!QFile::copy(source,dest)){QMessageBox::warning(this,"Import failed","Could not copy: "+source);continue;}
      QJsonObject s; s.insert("id",id);s.insert("label",info.completeBaseName());s.insert("path",dest);
      s.insert("color","#9F3655");s.insert("status","active");s.insert("volume",1.0);
      sounds.append(s);
    }
    save();refresh();
  }
  void editMenu(const QString &id,const QPoint &pos) {
    QMenu menu;
    auto *rename=menu.addAction("Rename");
    auto *color=menu.addAction("Button color");
    auto *archive=menu.addAction("Archive");
    auto *activate=menu.addAction("Activate");
    auto *retire=menu.addAction("Retire");
    auto *selected=menu.exec(pos);
    if(!selected)return;
    for(int i=0;i<sounds.size();++i) {
      auto s=sounds.at(i).toObject();if(s.value("id").toString()!=id)continue;
      if(selected==rename) {
        bool ok=false;QString value=QInputDialog::getText(this,"Sound label","Label:",QLineEdit::Normal,s.value("label").toString(),&ok);
        if(ok&&!value.trimmed().isEmpty())s.insert("label",value.trimmed());
      } else if(selected==color) {
        QColor c=QColorDialog::getColor(QColor(s.value("color").toString()),this,"Sound button color");
        if(c.isValid())s.insert("color",c.name());
      } else if(selected==archive) s.insert("status","archived");
      else if(selected==activate) s.insert("status","active");
      else if(selected==retire) s.insert("status","retired");
      sounds.replace(i,s);break;
    }
    save();refresh();
  }
  void manageLibrary() {
    QStringList entries;
    for(const auto &v:sounds){auto s=v.toObject();entries << s.value("label").toString()+" ["+s.value("status").toString("active")+"]";}
    if(entries.isEmpty()){QMessageBox::information(this,"Library","Add a sound to get started.");return;}
    bool ok=false;auto chosen=QInputDialog::getItem(this,"Manage Library","Choose a sound:",entries,0,false,&ok);
    if(!ok)return;
    int idx=entries.indexOf(chosen);if(idx<0)return;
    auto s=sounds.at(idx).toObject();
    QStringList states={"active","archived","retired"};
    auto state=QInputDialog::getItem(this,"Sound status","Move to:",states,states.indexOf(s.value("status").toString("active")),false,&ok);
    if(ok){s.insert("status",state);sounds.replace(idx,s);save();refresh();}
  }
};
QPointer<Soundboard> panel;
void onFrontendEvent(enum obs_frontend_event event,void*) {
  if(event==OBS_FRONTEND_EVENT_FINISHED_LOADING && !panel) {
    panel=new Soundboard();
    if(!obs_frontend_add_dock_by_id("masqrayd.soundboard.dock","Masqrayd Soundboard",panel)) {
      delete panel;panel=nullptr;
      blog(LOG_ERROR,"Masqrayd Soundboard: failed to register dock");
    }
  }
}
}
bool obs_module_load(void) {
  obs_frontend_add_event_callback(onFrontendEvent,nullptr);
  blog(LOG_INFO,"Masqrayd Soundboard prototype loaded");
  return true;
}
void obs_module_unload(void) {
  obs_frontend_remove_event_callback(onFrontendEvent,nullptr);
  // OBS frontend owns the registered dock widget.
}
