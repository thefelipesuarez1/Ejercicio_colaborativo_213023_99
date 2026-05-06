from abc import ABC, abstractmethod
import logging
from datetime import datetime


# CONFIGURACIÓN DE LOGS

logging.basicConfig(
    filename="sistema_gestion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# EXCEPCIONES PERSONALIZADAS

class SistemaError(Exception):
    pass

class ValidacionError(SistemaError):
    pass

class ServicioError(SistemaError):
    pass

class ReservaError(SistemaError):
    pass


# CLASE ABSTRACTA GENERAL

class Entidad(ABC):
    @abstractmethod
    def mostrar_info(self):
        pass


# CLASE CLIENTE

class Cliente(Entidad):
    def __init__(self, nombre, email, documento):
        self.__nombre = nombre
        self.__email = email
        self.__documento = documento
        self.validar()
        logging.info(f"Cliente creado correctamente: {self.__nombre}")

    def validar(self):
        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            raise ValidacionError("El nombre del cliente no puede estar vacío.")

        if not isinstance(self.__email, str) or "@" not in self.__email or "." not in self.__email:
            raise ValidacionError("El correo electrónico no es válido.")

        if not str(self.__documento).isdigit() or len(str(self.__documento)) < 6:
            raise ValidacionError("El documento debe ser numérico y tener mínimo 6 dígitos.")

    def mostrar_info(self):
        return f"Cliente: {self.__nombre} | Email: {self.__email} | Documento: {self.__documento}"

    def obtener_nombre(self):
        return self.__nombre


# CLASE ABSTRACTA SERVICIO

class Servicio(ABC):
    def __init__(self, nombre, costo_base, disponible=True):
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = disponible
        self.validar_servicio()

    def validar_servicio(self):
        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ServicioError("El nombre del servicio no puede estar vacío.")

        if not isinstance(self.costo_base, (int, float)) or self.costo_base <= 0:
            raise ServicioError("El costo base del servicio debe ser mayor que cero.")

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioError(f"El servicio '{self.nombre}' no se encuentra disponible.")


# SERVICIOS

class Sala(Servicio):
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ValidacionError("La cantidad de horas para la sala debe ser mayor que cero.")

        subtotal = self.costo_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise ValidacionError("El costo total no puede ser negativo.")

        return total

    def descripcion(self):
        return f"Reserva de sala: {self.nombre}"


class Equipo(Servicio):
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ValidacionError("La cantidad de días para el equipo debe ser mayor que cero.")

        subtotal = self.costo_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise ValidacionError("El costo total no puede ser negativo.")

        return total

    def descripcion(self):
        return f"Alquiler de equipo: {self.nombre}"


class Asesoria(Servicio):
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ValidacionError("La cantidad de horas de asesoría debe ser mayor que cero.")

        subtotal = self.costo_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise ValidacionError("El costo total no puede ser negativo.")

        return total

    def descripcion(self):
        return f"Asesoría especializada: {self.nombre}"


# CLASE RESERVA

class Reserva(Entidad):
    def __init__(self, cliente, servicio, duracion):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha_creacion = datetime.now()

    def confirmar(self):
        if self.estado == "Cancelada":
            raise ReservaError("No se puede confirmar una reserva cancelada.")

        self.estado = "Confirmada"
        logging.info("Reserva confirmada correctamente.")

    def cancelar(self):
        if self.estado == "Confirmada":
            raise ReservaError("No se puede cancelar una reserva ya confirmada.")

        self.estado = "Cancelada"
        logging.info("Reserva cancelada correctamente.")

    def procesar(self, impuesto=0, descuento=0):
        try:
            if not isinstance(self.cliente, Cliente):
                raise ReservaError("El cliente asociado a la reserva no es válido.")

            if not isinstance(self.servicio, Servicio):
                raise ReservaError("El servicio asociado a la reserva no es válido.")

            self.servicio.validar_disponibilidad()
            costo = self.servicio.calcular_costo(self.duracion, impuesto, descuento)

        except SistemaError as error:
            logging.error(f"Error controlado al procesar reserva: {error}")
            raise ReservaError("No fue posible procesar la reserva.") from error

        except Exception as error:
            logging.critical(f"Error inesperado en reserva: {error}")
            raise ReservaError("Error inesperado en el procesamiento de la reserva.") from error

        else:
            self.confirmar()
            logging.info(f"Reserva procesada exitosamente. Costo total: {costo}")
            return costo

        finally:
            logging.info("Finalizó intento de procesamiento de reserva.")

    def mostrar_info(self):
        return (
            f"{self.cliente.mostrar_info()} | "
            f"{self.servicio.descripcion()} | "
            f"Duración: {self.duracion} | "
            f"Estado: {self.estado}"
        )


# SISTEMA

class SistemaGestion:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, nombre, email, documento):
        try:
            cliente = Cliente(nombre, email, documento)

        except ValidacionError as error:
            logging.error(f"Error al registrar cliente: {error}")
            print(f"Error al registrar cliente: {error}")

        else:
            self.clientes.append(cliente)
            print("Cliente registrado correctamente.")
            print(cliente.mostrar_info())
            return cliente

        finally:
            logging.info("Finalizó operación de registro de cliente.")

    def agregar_servicio(self, servicio):
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioError("El objeto no corresponde a un servicio válido.")

            self.servicios.append(servicio)

        except ServicioError as error:
            logging.error(f"Error al agregar servicio: {error}")
            print(f"Error al agregar servicio: {error}")

        else:
            print("Servicio agregado correctamente.")
            print(servicio.descripcion())

        finally:
            logging.info("Finalizó operación de creación de servicio.")

    def crear_reserva(self, cliente, servicio, duracion, impuesto=0, descuento=0):
        try:
            reserva = Reserva(cliente, servicio, duracion)
            costo = reserva.procesar(impuesto, descuento)

        except ReservaError as error:
            logging.error(f"Error al crear reserva: {error}")
            print(f"Error al crear reserva: {error}")

        else:
            self.reservas.append(reserva)
            print("Reserva creada exitosamente.")
            print(reserva.mostrar_info())
            print(f"Costo total: ${costo}")

        finally:
            logging.info("Finalizó operación de reserva.")


# SIMULACIÓN

def ejecutar_simulacion():
    sistema = SistemaGestion()

    print("\n========== SISTEMA INTEGRAL SOFTWARE FJ ==========\n")

    print("\n----- REGISTRO DE CLIENTES -----")

    cliente1 = sistema.registrar_cliente("Luis Felipe Suárez Muñoz", "lfsuarezmu@unadvirtual.edu.co", "1017146556")
    cliente2 = sistema.registrar_cliente("Juan David Rivera Betancur", "jdriverabetancur27@unadvirtual.edu.co", "87654321")
    cliente3 = sistema.registrar_cliente("Luis Mariano Bedoya Velasquez", "luismaribedoya22@unadvirtual.edu.co", "11223344")
    cliente4 = sistema.registrar_cliente("Daniela Castro Chaverra", "danielacastrocha1@gmail.com", "12345678")

    sistema.registrar_cliente("", "correo@gmail.com", "123456")
    sistema.registrar_cliente("Cliente Sin Correo", "correo_invalido", "123456")
    sistema.registrar_cliente("Cliente Documento Malo", "cliente@gmail.com", "ABC123")

    print("\n----- CREACIÓN DE SERVICIOS -----")

    sala = Sala("Sala VIP", 50000)
    equipo = Equipo("Laptop Dell", 30000)
    asesoria = Asesoria("Consultoría en software", 100000)
    servicio_no_disponible = Sala("Sala de Conferencias", 80000, disponible=False)

    sistema.agregar_servicio(sala)
    sistema.agregar_servicio(equipo)
    sistema.agregar_servicio(asesoria)
    sistema.agregar_servicio(servicio_no_disponible)

    print("\n----- CREACIÓN DE RESERVAS -----")

    sistema.crear_reserva(cliente1, sala, 2)
    sistema.crear_reserva(cliente2, equipo, 3, impuesto=0.19)
    sistema.crear_reserva(cliente3, asesoria, 1, impuesto=0.19, descuento=20000)

    
    sistema.crear_reserva(cliente4, sala, 3, impuesto=0.19)

    sistema.crear_reserva(cliente1, sala, -1)
    sistema.crear_reserva(cliente2, equipo, 0)
    sistema.crear_reserva(cliente3, servicio_no_disponible, 2)

    print("\n=== RESUMEN ===")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas exitosas: {len(sistema.reservas)}")


if __name__ == "__main__":
    ejecutar_simulacion()

