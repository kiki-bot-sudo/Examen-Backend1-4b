from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Laptop


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


app = FastAPI()

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    if db.query(Laptop).first() is None:
        db.add_all([
            Laptop(id=1, marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
            Laptop(id=2, marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
            Laptop(id=3, marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True),
        ])
        db.commit()


@app.get("/")
def inicio():
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops")
def listar_laptops(db: Session = Depends(get_db)):
    return db.query(Laptop).order_by(Laptop.id).all()


@app.get("/laptops/disponibles")
def listar_laptops_disponibles(db: Session = Depends(get_db)):
    return db.query(Laptop).filter_by(disponible=True).order_by(Laptop.id).all()


@app.get("/laptops/{laptop_id}")
def obtener_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.get(Laptop, laptop_id)
    if laptop is None:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops")
def crear_laptop(datos: LaptopCreate, db: Session = Depends(get_db)):
    laptop = Laptop(
        marca=datos.marca,
        modelo=datos.modelo,
        ram_gb=datos.ram_gb,
        disponible=True,
    )
    db.add(laptop)
    db.commit()
    db.refresh(laptop)
    return laptop
