from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import jwt
from passlib.context import CryptContext

app = FastAPI(
    title="Сайт заказа услуг",
    description="REST API сервис с JWT аутентификацией (Вариант 4)",
    version="1.1.0"
)

# Настройки безопасности и JWT
SECRET_KEY = "grigalashvili_105"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема для извлечения токена из заголовка Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# In-memory хранилище (БД)
db_users = {}     
db_services = {}  
db_orders = {}    

# DTO
class UserBase(BaseModel):
    login: str = Field(..., description="Уникальный логин пользователя")
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str = Field(..., description="Пароль пользователя")

class UserResponse(UserBase):
    id: str

class ServiceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ServiceResponse(ServiceCreate):
    id: str

class OrderCreate(BaseModel):
    service_ids: List[str] 

class OrderResponse(BaseModel):
    id: str
    user_login: str
    services: List[ServiceResponse]
    total_price: float
    status: str

# Вспомогательные функции аутентификации
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные (неверный или просроченный токен)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db_users.get(username)
    if user is None:
        raise credentials_exception
    return user

# Auth API (Логин / Регистрация)
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth / Users"])
def register_user(user: UserCreate):
    """Регистрация нового пользователя"""
    if user.login in db_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь с таким логином уже существует"
        )
    
    user_id = str(uuid.uuid4())
    db_users[user.login] = {
        "id": user_id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "hashed_password": get_password_hash(user.password)
    }
    return db_users[user.login]

@app.post("/login", tags=["Auth / Users"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Аутентификация пользователя и выдача JWT токена"""
    user = db_users.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["login"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Users API (Публичные эндпоинты)
@app.get("/users/{login}", response_model=UserResponse, tags=["Users"])
def get_user_by_login(login: str):
    """Поиск пользователя по логину"""
    user = db_users.get(login)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@app.get("/users/search/", response_model=List[UserResponse], tags=["Users"])
def search_users(mask: str = Query(..., description="Маска для поиска по имени или фамилии")):
    """Поиск пользователя по маске имя и фамилии"""
    results = []
    mask_lower = mask.lower()
    for user in db_users.values():
        if mask_lower in user["first_name"].lower() or mask_lower in user["last_name"].lower():
            results.append(user)
    return results

# Service Catalog API
@app.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED, tags=["Services"])
def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    """Создание услуги (ТРЕБУЕТСЯ АВТОРИЗАЦИЯ)"""
    service_id = str(uuid.uuid4())
    new_service = {"id": service_id, **service.model_dump()}
    db_services[service_id] = new_service
    return new_service

@app.get("/services", response_model=List[ServiceResponse], tags=["Services"])
def get_all_services():
    """Получение списка всех услуг"""
    return list(db_services.values())

# Order Service API
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Добавление услуг в заказ (ТРЕБУЕТСЯ АВТОРИЗАЦИЯ)"""
    ordered_services = []
    total_price = 0.0
    for s_id in order.service_ids:
        service = db_services.get(s_id)
        if not service:
            raise HTTPException(status_code=404, detail=f"Услуга с ID '{s_id}' не найдена")
        ordered_services.append(service)
        total_price += service["price"]

    order_id = str(uuid.uuid4())
    new_order = {
        "id": order_id,
        "user_login": current_user["login"],
        "services": ordered_services,
        "total_price": total_price,
        "status": "CREATED"
    }
    db_orders[order_id] = new_order
    return new_order

@app.get("/orders/user/{login}", response_model=List[OrderResponse], tags=["Orders"])
def get_user_orders(login: str):
    """Получение заказов для пользователя"""
    user_orders = [order for order in db_orders.values() if order["user_login"] == login]
    return user_orders