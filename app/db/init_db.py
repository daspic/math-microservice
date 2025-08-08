from app.db.session import engine
from app.models.db_models import MathOperation


def init_db():
    MathOperation.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
