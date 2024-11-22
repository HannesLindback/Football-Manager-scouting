import sqlalchemy as sql
import sqlalchemy.orm as orm
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float
from sqlalchemy.types import BigInteger


class Base(orm.DeclarativeBase):
    pass


class Player(Base):

    __tablename__ = 'player'

    PlayerInfo: Mapped[List['PlayerInfo']] = relationship('PlayerInfo', back_populates='_player')
    Stats: Mapped[List['Stats']]           = relationship('Stats', back_populates='_player')
    Contract: Mapped[List['Contract']]     = relationship('Contract', back_populates='_player')
    Ca: Mapped[List['Ca']]                 = relationship('Ca', back_populates='_player')
    Attributes: Mapped[List['Attributes']] = relationship('Attributes', back_populates='_player')

    _id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    name: Mapped[str]   = mapped_column(String(50))
    uid: Mapped[str]    = mapped_column(String(50))
    season: Mapped[str] = mapped_column(String(20))
    

class PlayerInfo(Base):

    __tablename__ = 'playerInfo'

    age: Mapped[int]       = mapped_column(Integer)
    position: Mapped[int]  = mapped_column(Integer, sql.ForeignKey('position.id'))
    rightfoot: Mapped[int] = mapped_column(Integer, sql.ForeignKey('foot.id'))
    leftfoot: Mapped[int]  = mapped_column(Integer, sql.ForeignKey('foot.id'))
    mins: Mapped[int]      = mapped_column(Integer)
    division: Mapped[int]  = mapped_column(Integer, sql.ForeignKey('division.id'))
    club: Mapped[int]      = mapped_column(Integer, sql.ForeignKey('club.id'))
    nat: Mapped[int]       = mapped_column(Integer, sql.ForeignKey('nat.id'))
    eligible: Mapped[int]  = mapped_column(Integer, sql.ForeignKey('eligible.id'))

    _player: Mapped['Player']      = relationship('Player', back_populates='PlayerInfo')
    
    Position: Mapped['Position']   = relationship('Position', back_populates='_playerInfo')
    Rightfoot: Mapped['Foot']      = relationship('Foot', foreign_keys=[rightfoot], back_populates='_rightFootStrength')
    Leftfoot: Mapped['Foot']       = relationship('Foot', foreign_keys=[leftfoot], back_populates='_leftFootStrength')
    Division: Mapped['Division']   = relationship('Division', back_populates='_playerInfo')
    Club: Mapped['Club']           = relationship('Club', back_populates='_playerInfo')
    Nat: Mapped['Nat']             = relationship('Nat', back_populates='_playerInfo')
    Eligible: Mapped['Eligible']   = relationship('Eligible', back_populates='_playerInfo')
    
    
    
    _id: Mapped[int]       = mapped_column(primary_key=True, autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))


class Position(Base):
    
    __tablename__ = 'position'
    
    _playerInfo: Mapped['PlayerInfo'] = relationship('PlayerInfo')
    id: Mapped[int]       = mapped_column(primary_key=True, autoincrement=True)
    position: Mapped[str] = mapped_column(String(100))
    

class Nat(Base):
    
    __tablename__ = 'nat'
    
    _playerInfo: Mapped['PlayerInfo'] = relationship('PlayerInfo')
    id: Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    nat: Mapped[str] = mapped_column(String(100))
    
    
class Division(Base):
    
    __tablename__ = 'division'
    
    _playerInfo: Mapped['PlayerInfo'] = relationship('PlayerInfo')
    id: Mapped[int]       = mapped_column(primary_key=True, autoincrement=True)
    division: Mapped[str] = mapped_column(String(100))
    
    
class Club(Base):
    
    __tablename__ = 'club'
    
    _playerInfo: Mapped['PlayerInfo'] = relationship('PlayerInfo')
    id: Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    club: Mapped[str] = mapped_column(String(100))
    

class Foot(Base):
    
    __tablename__ = 'foot'
    
    id: Mapped[int]    = mapped_column(primary_key=True, autoincrement=True)
    foot: Mapped[str]  = mapped_column(String(100))
    
    _rightFootStrength = relationship('PlayerInfo', foreign_keys=PlayerInfo.rightfoot)
    _leftFootStrength  = relationship('PlayerInfo', foreign_keys=PlayerInfo.leftfoot)


class Eligible(Base):
    
    __tablename__ = 'eligible'
    
    _playerInfo: Mapped['PlayerInfo'] = relationship('PlayerInfo')
    
    id: Mapped[int]       = mapped_column(primary_key=True, autoincrement=True)
    eligible: Mapped[str] = mapped_column(String(100))


class Stats(Base):

    __tablename__ = 'stats'

    _id: Mapped[int]          = mapped_column(primary_key=True, autoincrement=True)
    _playerID: Mapped[int]    = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='Stats')

    aerA: Mapped[float]          = mapped_column(Float(16))
    hdrsW: Mapped[float]         = mapped_column(Float(16))
    blk: Mapped[float]           = mapped_column(Float(16))
    clr: Mapped[float]           = mapped_column(Float(16))
    tckC: Mapped[float]          = mapped_column(Float(16))
    presA: Mapped[float]         = mapped_column(Float(16))
    presC: Mapped[float]         = mapped_column(Float(16))
    interceptions: Mapped[float] = mapped_column(Float(16))
    sprints: Mapped[float]       = mapped_column(Float(16))
    possLost: Mapped[float]      = mapped_column(Float(16))
    possWon: Mapped[float]       = mapped_column(Float(16))
    drb: Mapped[float]           = mapped_column(Float(16))
    opCrsA: Mapped[float]        = mapped_column(Float(16))
    opCrsC: Mapped[float]        = mapped_column(Float(16))
    psA: Mapped[float]           = mapped_column(Float(16))
    psC: Mapped[float]           = mapped_column(Float(16))
    prPasses: Mapped[float]      = mapped_column(Float(16))
    opKp: Mapped[float]          = mapped_column(Float(16))
    chC: Mapped[float]           = mapped_column(Float(16))
    xa: Mapped[float]            = mapped_column(Float(16))
    shot: Mapped[float]          = mapped_column(Float(16))
    sht: Mapped[float]           = mapped_column(Float(16))
    npXg: Mapped[float]          = mapped_column(Float(16))


class Attributes(Base):

    __tablename__ = 'attributes'

    _player: Mapped['Player'] = relationship('Player', back_populates='Attributes')

    _id: Mapped[int]          = mapped_column(primary_key=True, autoincrement=True)
    _playerID: Mapped[int]    = mapped_column(Integer, sql.ForeignKey('player._id'))

    cor: Mapped[str]       = mapped_column(String(5))
    cro: Mapped[str]       = mapped_column(String(5))
    dri: Mapped[str]       = mapped_column(String(5))
    fin: Mapped[str]       = mapped_column(String(5))
    fir: Mapped[str]       = mapped_column(String(5))
    fre: Mapped[str]       = mapped_column(String(5))
    hea: Mapped[str]       = mapped_column(String(5))
    lon: Mapped[str]       = mapped_column(String(5))
    lth: Mapped[str]       = mapped_column(String(5))
    mar: Mapped[str]       = mapped_column(String(5))
    pas: Mapped[str]       = mapped_column(String(5))
    pen: Mapped[str]       = mapped_column(String(5))
    tck: Mapped[str]       = mapped_column(String(5))
    tec: Mapped[str]       = mapped_column(String(5))
    agg: Mapped[str]       = mapped_column(String(5))
    ant: Mapped[str]       = mapped_column(String(5))
    bra: Mapped[str]       = mapped_column(String(5))
    cmp: Mapped[str]       = mapped_column(String(5))
    cnt: Mapped[str]       = mapped_column(String(5))
    decisions: Mapped[str] = mapped_column(String(5))
    det: Mapped[str]       = mapped_column(String(5))
    fla: Mapped[str]       = mapped_column(String(5))
    ldr: Mapped[str]       = mapped_column(String(5))
    otb: Mapped[str]       = mapped_column(String(5))
    pos: Mapped[str]       = mapped_column(String(5))
    tea: Mapped[str]       = mapped_column(String(5))
    vis: Mapped[str]       = mapped_column(String(5))
    wor: Mapped[str]       = mapped_column(String(5))
    acc: Mapped[str]       = mapped_column(String(5))
    agi: Mapped[str]       = mapped_column(String(5))
    bal: Mapped[str]       = mapped_column(String(5))
    jum: Mapped[str]       = mapped_column(String(5))
    natF: Mapped[str]      = mapped_column(String(5))
    pac: Mapped[str]       = mapped_column(String(5))
    sta: Mapped[str]       = mapped_column(String(5))
    strength: Mapped[str]  = mapped_column(String(5))
    aer: Mapped[str]       = mapped_column(String(5))
    cmd: Mapped[str]       = mapped_column(String(5))
    com: Mapped[str]       = mapped_column(String(5))
    ecc: Mapped[str]       = mapped_column(String(5))
    han: Mapped[str]       = mapped_column(String(5))
    kic: Mapped[str]       = mapped_column(String(5))
    oneVsOne: Mapped[str]  = mapped_column(String(5))
    pun: Mapped[str]       = mapped_column(String(5))
    ref: Mapped[str]       = mapped_column(String(5))
    tro: Mapped[str]       = mapped_column(String(5))
    thr: Mapped[str]       = mapped_column(String(5))


class Ca(Base):

    __tablename__ = 'ca'

    _id: Mapped[int]          = mapped_column(primary_key=True, autoincrement=True)
    _playerID: Mapped[int]    = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='Ca')

    ca: Mapped[int] = mapped_column(Integer)


class Contract(Base):

    __tablename__ = 'contract'

    _id: Mapped[int]          = mapped_column(primary_key=True, autoincrement=True)
    _playerID: Mapped[int]    = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='Contract')
    
    beginDate: Mapped[int]        = mapped_column(Integer) 
    expiryDate: Mapped[int]       = mapped_column(Integer)
    extension: Mapped[int]        = mapped_column(Integer)
    wage: Mapped[int]             = mapped_column(BigInteger)
    value: Mapped[int]            = mapped_column(BigInteger)
    releaseClauseFee: Mapped[int] = mapped_column(BigInteger)
