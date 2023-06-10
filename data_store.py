# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_database

metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_database)


class Viewed(Base):
    __tablename__ = 'viewed'  # имя таблицы
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        return f'{self.profile_id} - {self.worksheet_id}'


class Database:
    def __init__(self):
        self.engine = engine
        self.metadata = metadata  # метаданные
        Base.metadata.create_all(self.engine)  # создание таблицы

    # добавление записи в БД
    def add_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
            session.add(to_bd)  # добавление записи в БД
            session.commit()

    def request_user(self, profile_id: int, worksheet_id: int) -> bool:  # проверка наличия записи в БД
        with Session(self.engine) as session:
            to_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id,
                                                 Viewed.worksheet_id == worksheet_id).first()  # получение записи из БД
            if to_bd:
                return True
            else:
                return False  # проверка наличия записи в БД

    # извлечение записей из БД
    def check_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            from_bd = session.query(Viewed).filter(
                Viewed.profile_id == profile_id,
                Viewed.worksheet_id == worksheet_id
            ).first()  # получение записи из БД
            return True if from_bd else False  # проверка наличия записи в БД


if __name__ == '__main__':
    engine = create_engine(db_database)
    Base.metadata.create_all(engine)
