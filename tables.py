"""Module for creating a Declarative base mapping of a database's tables using Sqlalchemy's ORM."""

import sqlalchemy as sql
import sqlalchemy.orm as orm
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import String, Integer, Float
from sqlalchemy.types import BigInteger


class Base(orm.DeclarativeBase):
    pass


class Player(Base):

    __tablename__ = 'player'

    _id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=False)
    _playerInfo: Mapped[List['PlayerInfo']] = relationship('PlayerInfo', back_populates='_player')
    _stats: Mapped[List['Stats']] = relationship('Stats', back_populates='_player')
    _contract: Mapped[List['Contract']] = relationship('Contract', back_populates='_player')
    _ca: Mapped[List['Ca']] = relationship('Ca', back_populates='_player')
    _attributes: Mapped[List['Attributes']] = relationship('Attributes', back_populates='_player')
    
    name: Mapped[str] = mapped_column(String(50))
    UID: Mapped[str] = mapped_column(String(50))

    


class PlayerInfo(Base):

    __tablename__ = 'playerInfo'

    _id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='_playerInfo')

    age: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String(100))
    rightFoot: Mapped[str] = mapped_column(String(100))
    leftFoot: Mapped[str] = mapped_column(String(100))
    mins: Mapped[str] = mapped_column(Integer)
    division: Mapped[str] = mapped_column(String(100))
    club: Mapped[str] = mapped_column(String(100))
    nat: Mapped[str] = mapped_column(String(5))
    eligible: Mapped[str] = mapped_column(String(5))


class Stats(Base):

    __tablename__ = 'stats'

    _id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='_stats')

    aerA: Mapped[float] = mapped_column(Float(16))
    hdrsW: Mapped[float] = mapped_column(Float(16))
    blk: Mapped[float] = mapped_column(Float(16))
    clr: Mapped[float] = mapped_column(Float(16))
    tckC: Mapped[float] = mapped_column(Float(16))
    presA: Mapped[float] = mapped_column(Float(16))
    presC: Mapped[float] = mapped_column(Float(16))
    interceptions: Mapped[float] = mapped_column(Float(16))
    sprints: Mapped[float] = mapped_column(Float(16))
    possLost: Mapped[float] = mapped_column(Float(16))
    possWon: Mapped[float] = mapped_column(Float(16))
    drb: Mapped[float] = mapped_column(Float(16))
    opCrsA: Mapped[float] = mapped_column(Float(16))
    opCrsC: Mapped[float] = mapped_column(Float(16))
    psA: Mapped[float] = mapped_column(Float(16))
    psC: Mapped[float] = mapped_column(Float(16))
    prPasses: Mapped[float] = mapped_column(Float(16))
    opKp: Mapped[float] = mapped_column(Float(16))
    chC: Mapped[float] = mapped_column(Float(16))
    xa: Mapped[float] = mapped_column(Float(16))
    shot: Mapped[float] = mapped_column(Float(16))
    sht: Mapped[float] = mapped_column(Float(16))
    npXg: Mapped[float] = mapped_column(Float(16))


class Attributes(Base):

    __tablename__ = 'attributes'

    _id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='_attributes')

    cor: Mapped[str] = mapped_column(String(5))
    cro: Mapped[str] = mapped_column(String(5))
    dri: Mapped[str] = mapped_column(String(5))
    fin: Mapped[str] = mapped_column(String(5))
    fir: Mapped[str] = mapped_column(String(5))
    fre: Mapped[str] = mapped_column(String(5))
    hea: Mapped[str] = mapped_column(String(5))
    lon: Mapped[str] = mapped_column(String(5))
    lth: Mapped[str] = mapped_column(String(5))
    mar: Mapped[str] = mapped_column(String(5))
    pas: Mapped[str] = mapped_column(String(5))
    pen: Mapped[str] = mapped_column(String(5))
    tck: Mapped[str] = mapped_column(String(5))
    tec: Mapped[str] = mapped_column(String(5))
    agg: Mapped[str] = mapped_column(String(5))
    ant: Mapped[str] = mapped_column(String(5))
    bra: Mapped[str] = mapped_column(String(5))
    cmp: Mapped[str] = mapped_column(String(5))
    cnt: Mapped[str] = mapped_column(String(5))
    decisions: Mapped[str] = mapped_column(String(5))
    det: Mapped[str] = mapped_column(String(5))
    fla: Mapped[str] = mapped_column(String(5))
    ldr: Mapped[str] = mapped_column(String(5))
    otb: Mapped[str] = mapped_column(String(5))
    pos: Mapped[str] = mapped_column(String(5))
    tea: Mapped[str] = mapped_column(String(5))
    vis: Mapped[str] = mapped_column(String(5))
    wor: Mapped[str] = mapped_column(String(5))
    acc: Mapped[str] = mapped_column(String(5))
    agi: Mapped[str] = mapped_column(String(5))
    bal: Mapped[str] = mapped_column(String(5))
    jum: Mapped[str] = mapped_column(String(5))
    natF: Mapped[str] = mapped_column(String(5))
    pac: Mapped[str] = mapped_column(String(5))
    sta: Mapped[str] = mapped_column(String(5))
    strength: Mapped[str] = mapped_column(String(5))
    aer: Mapped[str] = mapped_column(String(5))
    cmd: Mapped[str] = mapped_column(String(5))
    com: Mapped[str] = mapped_column(String(5))
    ecc: Mapped[str] = mapped_column(String(5))
    han: Mapped[str] = mapped_column(String(5))
    kic: Mapped[str] = mapped_column(String(5))
    oneVsOne: Mapped[str] = mapped_column(String(5))
    pun: Mapped[str] = mapped_column(String(5))
    ref: Mapped[str] = mapped_column(String(5))
    tro: Mapped[str] = mapped_column(String(5))
    thr: Mapped[str] = mapped_column(String(5))


class Ca(Base):

    __tablename__ = 'ca'

    _id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='_ca')

    ca: Mapped[int] = mapped_column(Integer)


class Contract(Base):

    __tablename__ = 'contract'

    _id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    _playerID: Mapped[int] = mapped_column(Integer, sql.ForeignKey('player._id'))
    _player: Mapped['Player'] = relationship('Player', back_populates='_contract')
    
    beginDate: Mapped[int] = mapped_column(Integer) 
    expiryDate: Mapped[int] = mapped_column(Integer)
    extension: Mapped[int] = mapped_column(Integer)
    wage: Mapped[int] = mapped_column(BigInteger)
    value: Mapped[int] = mapped_column(BigInteger)
    releaseClauseFee: Mapped[int] = mapped_column(BigInteger)
