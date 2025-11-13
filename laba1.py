import json
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any

# Базовые классы для компонентов
class Engine:
    def __init__(self, type: str, power: float):
        self.type = type
        self.power = power
    
    def start(self) -> str:
        return f"{self.type} engine started"
    
    def get_info(self) -> Dict[str, Any]:
        return {"type": self.type, "power": self.power}

class Transmission:
    def __init__(self, type: str, gears: int):
        self.type = type
        self.gears = gears
    
    def shift(self, gear: int) -> str:
        return f"Shifted to gear {gear}"
    
    def get_info(self) -> Dict[str, Any]:  # ДОБАВЛЕН ОТСУТСТВУЮЩИЙ МЕТОД
        return {"type": self.type, "gears": self.gears}

class ElectricEngine(Engine):
    def __init__(self, power: float, battery_capacity: float):
        super().__init__("Electric", power)
        self.battery_capacity = battery_capacity
    
    def start(self) -> str:
        return "Electric engine started silently"
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info["battery_capacity"] = self.battery_capacity
        return info

class CombustionEngine(Engine):
    def __init__(self, power: float, fuel_type: str):
        super().__init__("Combustion", power)
        self.fuel_type = fuel_type
    
    def start(self) -> str:
        return f"Combustion engine started with {self.fuel_type}"
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info["fuel_type"] = self.fuel_type
        return info

class AutoTransmission(Transmission):
    def __init__(self, gears: int, mode: str = "Normal"):
        super().__init__("Automatic", gears)
        self.mode = mode
    
    def shift(self, gear: int) -> str:
        if 1 <= gear <= self.gears:
            return f"Automatically shifted to gear {gear} in {self.mode} mode"
        return "Invalid gear"
    
    def get_info(self) -> Dict[str, Any]:  # ДОБАВЛЕН МЕТОД
        info = super().get_info()
        info["mode"] = self.mode
        return info

class ManualTransmission(Transmission):
    def __init__(self, gears: int, clutch_type: str):
        super().__init__("Manual", gears)
        self.clutch_type = clutch_type
    
    def shift(self, gear: int) -> str:
        if 1 <= gear <= self.gears:
            return f"Manually shifted to gear {gear} using {self.clutch_type} clutch"
        return "Invalid gear"
    
    def get_info(self) -> Dict[str, Any]:  # ДОБАВЛЕН МЕТОД
        info = super().get_info()
        info["clutch_type"] = self.clutch_type
        return info

# Основной класс Vehicle
class Vehicle:
    def __init__(
        self,
        id: str,
        brand: str,
        model: str,
        year: int,
        engine: Engine,
        transmission: Transmission
    ):
        self.id = id
        self.brand = brand
        self.model = model
        self.year = year
        self.engine = engine
        self.transmission = transmission
    
    def start(self) -> str:
        return f"{self.brand} {self.model}: {self.engine.start()}"
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "engine": self.engine.get_info(),
            "transmission": self.transmission.get_info()  # Теперь этот метод существует
        }
    
    def to_dict(self) -> dict:
        """Сериализация в словарь для JSON"""
        return self.get_info()

    @classmethod
    def from_dict(cls, data: dict) -> 'Vehicle':
        """Десериализация из словаря"""
        engine_data = data["engine"]
        transmission_data = data["transmission"]
        
        # Создание двигателя
        if engine_data["type"] == "Electric":
            engine = ElectricEngine(
                power=engine_data["power"],
                battery_capacity=engine_data["battery_capacity"]
            )
        else:
            engine = CombustionEngine(
                power=engine_data["power"],
                fuel_type=engine_data["fuel_type"]
            )
        
        # Создание трансмиссии
        if transmission_data["type"] == "Automatic":
            transmission = AutoTransmission(
                gears=transmission_data["gears"],
                mode=transmission_data.get("mode", "Normal")
            )
        else:
            transmission = ManualTransmission(
                gears=transmission_data["gears"],
                clutch_type=transmission_data["clutch_type"]
            )
        
        return cls(
            id=data["id"],
            brand=data["brand"],
            model=data["model"],
            year=data["year"],
            engine=engine,
            transmission=transmission
        )

# Производные классы транспортных средств
class Car(Vehicle):
    def __init__(
        self,
        id: str,
        brand: str,
        model: str,
        year: int,
        engine: Engine,
        transmission: Transmission,
        body_type: str
    ):
        super().__init__(id, brand, model, year, engine, transmission)
        self.body_type = body_type
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info["body_type"] = self.body_type
        info["vehicle_type"] = "Car"
        return info

class Truck(Vehicle):
    def __init__(
        self,
        id: str,
        brand: str,
        model: str,
        year: int,
        engine: Engine,
        transmission: Transmission,
        load_capacity: float
    ):
        super().__init__(id, brand, model, year, engine, transmission)
        self.load_capacity = load_capacity
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info["load_capacity"] = self.load_capacity
        info["vehicle_type"] = "Truck"
        return info

# Менеджер для CRUD операций
class VehicleManager:
    def __init__(self):
        self.laba1: List[Vehicle] = []
    
    def create(self, vehicle: Vehicle) -> None:
        """Создание нового транспортного средства"""
        self.laba1.append(vehicle)
        print(f"Vehicle {vehicle.id} created successfully")
    
    def read(self, id: str) -> Optional[Vehicle]:
        """Чтение транспортного средства по ID"""
        for vehicle in self.laba1:
            if vehicle.id == id:
                return vehicle
        print(f"Vehicle with id {id} not found")
        return None
    
    def read_all(self) -> List[Vehicle]:
        """Получение всех транспортных средств"""
        return self.laba1.copy()
    
    def update(self, id: str, **kwargs) -> bool:
        """Обновление транспортного средства"""
        vehicle = self.read(id)
        if vehicle:
            for key, value in kwargs.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)
                else:
                    print(f"Warning: {key} is not a valid attribute")
            print(f"Vehicle {id} updated successfully")
            return True
        return False
    
    def delete(self, id: str) -> bool:
        """Удаление транспортного средства"""
        vehicle = self.read(id)
        if vehicle:
            self.laba1.remove(vehicle)
            print(f"Vehicle {id} deleted successfully")
            return True
        return False
    
    def save_to_json(self, filename: str) -> None:
        """Сохранение в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([v.to_dict() for v in self.laba1], f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename} successfully")
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def load_from_json(self, filename: str) -> None:
        """Загрузка из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.laba1 = [Vehicle.from_dict(item) for item in data]
            print(f"Data loaded from {filename} successfully")
        except Exception as e:
            print(f"Error loading from JSON: {e}")

# Пример использования
def main():
    """Демонстрация работы системы"""
    manager = VehicleManager()
    
    # Создание различных транспортных средств
    print("=== Creating laba1 ===")
    
    electric_car = Car(
        id="1",
        brand="Tesla",
        model="Model S",
        year=2023,
        engine=ElectricEngine(power=150, battery_capacity=75.0),
        transmission=AutoTransmission(gears=1, mode="Eco"),
        body_type="Sedan"
    )
    
    combustion_car = Car(
        id="2",
        brand="Toyota",
        model="Camry",
        year=2022,
        engine=CombustionEngine(power=203, fuel_type="Petrol"),
        transmission=ManualTransmission(gears=6, clutch_type="Hydraulic"),
        body_type="Sedan"
    )
    combustion_car2 = Car(
        id="3",
        brand="honda",
        model="x",
        year=2025,
        engine=CombustionEngine(power=190, fuel_type="Petrol"),
        transmission=ManualTransmission(gears=6, clutch_type="Hydraulic"),
        body_type="Sedan"
    )
    
    # CRUD операции
    manager.create(electric_car)
    manager.create(combustion_car)
    manager.create(combustion_car2)
    
    print("\n=== Testing vehicle operations ===")
    # Тестирование методов транспортных средств
    for vehicle in manager.read_all():
        print(f"{vehicle.start()} | Info: {vehicle.get_info()}")
    
    print("\n=== Testing CRUD operations ===")
    # Чтение
    found_vehicle = manager.read("2")
    if found_vehicle:
        print(f"Found vehicle: {found_vehicle.brand} {found_vehicle.model}")
    
    # Сохранение данных
    print("\n=== Saving data ===")
    manager.save_to_json("laba1.json")
    
    # Демонстрация загрузки
    print("\n=== Testing data loading ===")
    new_manager = VehicleManager()
    new_manager.load_from_json("laba1.json")
    
    print(f"Loaded {len(new_manager.read_all())} laba1:")
    for vehicle in new_manager.read_all():
        print(f"- {vehicle.brand} {vehicle.model} ({vehicle.year})")

if __name__ == "__main__":
    main()