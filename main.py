from abc import ABC, abstractmethod
from typing import List, Optional

# ==============================================================================
# 1. GESTIÓN DE PROYECTOS (Composite, Strategy, Observer)
# ==============================================================================

class ObservadorProyecto(ABC):
    @abstractmethod
    def actualizar(self, mensaje: str) -> None:
        pass

class LiderProyectoObserver(ObservadorProyecto):
    def __init__(self, email: str):
        self.email = email

    def actualizar(self, mensaje: str) -> None:
        print(f"[Notificación Líder ({self.email})]: {mensaje}")

class ClienteObserver(ObservadorProyecto):
    def __init__(self, email: str):
        self.email = email

    def actualizar(self, mensaje: str) -> None:
        print(f"[Notificación Cliente ({self.email})]: {mensaje}")


class EstrategiaCosto(ABC):
    @abstractmethod
    def calcular_costo(self, horas: int, costo_base: float) -> float:
        pass

class CostoPorHoras(EstrategiaCosto):
    def __init__(self, tarifa_hora: float = 50.0):
        self.tarifa_hora = tarifa_hora

    def calcular_costo(self, horas: int, costo_base: float) -> float:
        return costo_base + (horas * self.tarifa_hora)

class CostoPorPuntosFuncion(EstrategiaCosto):
    def __init__(self, valor_punto: float = 120.0):
        self.valor_punto = valor_punto

    def calcular_costo(self, horas: int, costo_base: float) -> float:
        puntos_estimados = horas / 5  # Estimación basada en esfuerzo
        return costo_base + (puntos_estimados * self.valor_punto)


class ComponenteProyecto(ABC):
    @abstractmethod
    def get_costo(self, estrategia: EstrategiaCosto) -> float:
        pass

    @abstractmethod
    def get_tiempo_estimado(self) -> int:
        pass


class Tarea(ComponenteProyecto):
    def __init__(self, descripcion: str, costo_base: float, horas: int):
        self.descripcion = descripcion
        self.costo_base = costo_base
        self.horas = horas
        self.estado = "En Progreso"
        self.subtareas: List[ComponenteProyecto] = []

    def agregar_subtarea(self, subtarea: ComponenteProyecto):
        self.subtareas.append(subtarea)

    def cambiar_estado(self, nuevo_estado: str, proyecto: 'Proyecto'):
        self.estado = nuevo_estado
        print(f"-> Estado de tarea '{self.descripcion}' cambiado a: {nuevo_estado}")
        if nuevo_estado == "Completado":
            proyecto.notificar(f"La tarea '{self.descripcion}' ha sido COMPLETADA.")

    def get_costo(self, estrategia: EstrategiaCosto) -> float:
        costo = estrategia.calcular_costo(self.horas, self.costo_base)
        for st in self.subtareas:
            costo += st.get_costo(estrategia)
        return costo

    def get_tiempo_estimado(self) -> int:
        tiempo = self.horas
        for st in self.subtareas:
            tiempo += st.get_tiempo_estimado()
        return tiempo


class Fase(ComponenteProyecto):
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.elementos: List[ComponenteProyecto] = []

    def agregar_elemento(self, elem: ComponenteProyecto):
        self.elementos.append(elem)

    def get_costo(self, estrategia: EstrategiaCosto) -> float:
        return sum(e.get_costo(estrategia) for e in self.elementos)

    def get_tiempo_estimado(self) -> int:
        return sum(e.get_tiempo_estimado() for e in self.elementos)


class Proyecto(ComponenteProyecto):
    def __init__(self, id_proj: str, nombre: str, estrategia: EstrategiaCosto):
        self.id_proj = id_proj
        self.nombre = nombre
        self.estrategia = estrategia
        self.fases: List[ComponenteProyecto] = []
        self.observadores: List[ObservadorProyecto] = []

    def agregar_fase(self, fase: ComponenteProyecto):
        self.fases.append(fase)

    def set_estrategia(self, estrategia: EstrategiaCosto):
        self.estrategia = estrategia
        print(f"[Proyecto] Estrategia de estimación cambiada a: {estrategia.__class__.__name__}")

    def suscribir(self, obs: ObservadorProyecto):
        self.observadores.append(obs)

    def notificar(self, mensaje: str):
        for obs in self.observadores:
            obs.actualizar(mensaje)

    def get_costo(self, estrategia: Optional[EstrategiaCosto] = None) -> float:
        est = estrategia or self.estrategia
        return sum(f.get_costo(est) for f in self.fases)

    def get_tiempo_estimado(self) -> int:
        return sum(f.get_tiempo_estimado() for f in self.fases)


# ==============================================================================
# 2. MANEJO DE PERSONAL (Decorator, State)
# ==============================================================================

class EstadoEmpleado(ABC):
    @abstractmethod
    def puede_asignarse(self) -> bool:
        pass

class EnDisponibilidadState(EstadoEmpleado):
    def puede_asignarse(self) -> bool: return True

class AsignadoAProyectoState(EstadoEmpleado):
    def puede_asignarse(self) -> bool: return False

class EnLicenciaState(EstadoEmpleado):
    def puede_asignarse(self) -> bool: return False


class Empleado(ABC):
    @abstractmethod
    def get_salario(self) -> float:
        pass

    @abstractmethod
    def get_permisos(self) -> List[str]:
        pass

class EmpleadoBase(Empleado):
    def __init__(self, id_emp: str, nombre: str, salario_base: float):
        self.id_emp = id_emp
        self.nombre = nombre
        self.salario_base = salario_base
        self.estado: EstadoEmpleado = EnDisponibilidadState()

    def set_estado(self, estado: EstadoEmpleado):
        self.estado = estado

    def get_salario(self) -> float:
        return self.salario_base

    def get_permisos(self) -> List[str]:
        return ["Lectura", "Ejecución Tareas"]


class DecoradorResponsabilidad(Empleado):
    def __init__(self, empleado: Empleado):
        self.empleado_decorado = empleado

    def get_salario(self) -> float:
        return self.empleado_decorado.get_salario()

    def get_permisos(self) -> List[str]:
        return self.empleado_decorado.get_permisos()


class LiderTecnicoDecorator(DecoradorResponsabilidad):
    def get_salario(self) -> float:
        return super().get_salario() + 1200.0

    def get_permisos(self) -> List[str]:
        return super().get_permisos() + ["Aprobación Código", "Asignación Tareas"]


class SoporteFinDeSemanaDecorator(DecoradorResponsabilidad):
    def get_salario(self) -> float:
        return super().get_salario() + 500.0

    def get_permisos(self) -> List[str]:
        return super().get_permisos() + ["Acceso Guardia Servidores"]


# ==============================================================================
# 3. PIPELINE Y PRUEBAS (Chain of Responsibility, Factory Method)
# ==============================================================================

class PaquetePruebas:
    def __init__(self, tecnologia: str, archivos: List[str]):
        self.tecnologia = tecnologia
        self.archivos = archivos


class FasePrueba(ABC):
    def __init__(self):
        self.siguiente: Optional['FasePrueba'] = None

    def set_siguiente(self, siguiente: 'FasePrueba') -> 'FasePrueba':
        self.siguiente = siguiente
        return siguiente

    def ejecutar_pipeline(self, paquete: PaquetePruebas) -> bool:
        if not self._realizar_prueba(paquete):
            print(f"[Pipeline FALLIDO] Se detiene en: {self.__class__.__name__}")
            return False
        print(f"[Pipeline OK] {self.__class__.__name__} superada.")
        if self.siguiente:
            return self.siguiente.ejecutar_pipeline(paquete)
        return True

    @abstractmethod
    def _realizar_prueba(self, paquete: PaquetePruebas) -> bool:
        pass


class AnalisisEstatico(FasePrueba):
    def _realizar_prueba(self, paquete: PaquetePruebas) -> bool:
        return True

class PruebasUnitarias(FasePrueba):
    def _realizar_prueba(self, paquete: PaquetePruebas) -> bool:
        return True

class PruebasIntegracion(FasePrueba):
    def _realizar_prueba(self, paquete: PaquetePruebas) -> bool:
        return True

class PruebasSeguridad(FasePrueba):
    def _realizar_prueba(self, paquete: PaquetePruebas) -> bool:
        return True


class FabricaPaquetes(ABC):
    @abstractmethod
    def crear_paquete(self) -> PaquetePruebas:
        pass

class FabricaWeb(FabricaPaquetes):
    def crear_paquete(self) -> PaquetePruebas:
        return PaquetePruebas("Web", ["index.html", "app.js"])

class FabricaMobile(FabricaPaquetes):
    def crear_paquete(self) -> PaquetePruebas:
        return PaquetePruebas("Mobile", ["MainActivity.kt", "build.gradle"])


# ==============================================================================
# 4. CONTROL DE CAMBIOS Y MEDIADOR (Command, Mediator)
# ==============================================================================

class OrdenCambio(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class ModificarRequerimientoCommand(OrdenCambio):
    def __init__(self, proyecto: Proyecto, req_nuevo: str):
        self.proyecto = proyecto
        self.req_nuevo = req_nuevo
        self.req_anterior = "Requerimiento Base V1"

    def execute(self) -> None:
        print(f"[Command Executed] Modificando requerimiento a: '{self.req_nuevo}'")

    def undo(self) -> None:
        print(f"[Command Undo] Revertido requerimiento a: '{self.req_anterior}'")


class InvocadorComandos:
    def __init__(self):
        self.historial: List[OrdenCambio] = []

    def ejecutar_orden(self, cmd: OrdenCambio):
        cmd.execute()
        self.historial.append(cmd)

    def deshacer_ultimo(self):
        if self.historial:
            cmd = self.historial.pop()
            cmd.undo()
        else:
            print("[Command] No hay ordenes para deshacer.")


class MediadorCentral(ABC):
    @abstractmethod
    def notificar(self, emisor: object, evento: str) -> None:
        pass

class MediadorProyecto(MediadorCentral):
    def notificar(self, emisor: object, evento: str) -> None:
        print(f"[Mediator Central] Evento '{evento}' recibido desde {emisor.__class__.__name__}. Coordinando submodulos...")


# ==============================================================================
# 5. INFRAESTRUCTURA Y FACADE (Adapter, Singleton, Facade)
# ==============================================================================

class ConfiguracionSistema:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.parametros = {"entorno": "Produccion", "version": "1.0.0"}
        return cls._instancia


class ServicioCalendario(ABC):
    @abstractmethod
    def agendar_reunion(self, fecha: str, titulo: str) -> None:
        pass

class AdaptadorGoogleCalendar(ServicioCalendario):
    def agendar_reunion(self, fecha: str, titulo: str) -> None:
        print(f"[Google Calendar API] Reunión '{titulo}' agendada para el {fecha}.")


class DevEnterpriseOSFacade:
    def __init__(self):
        self.config = ConfiguracionSistema()
        self.mediador = MediadorProyecto()
        self.calendario = AdaptadorGoogleCalendar()
        self.invocador = InvocadorComandos()

    def demo_sistema(self):
        print("==================================================")
        print("      DEVENTERPRISE OS - DEMO DE OPERACIÓN        ")
        print("==================================================\n")

        # 1. Configuración Singleton & Proyecto
        print(f"Configuración cargada en versión: {self.config.parametros['version']}")
        
        estrategia_horas = CostoPorHoras(tarifa_hora=60.0)
        proyecto = Proyecto("P-001", "Sistema ERP Cliente X", estrategia_horas)
        
        # Suscribir observadores
        lider = LiderProyectoObserver("lider@deventerprise.com")
        cliente = ClienteObserver("cliente@clientex.com")
        proyecto.suscribir(lider)
        proyecto.suscribir(cliente)

        # 2. Construcción Jerárquica Composite
        fase_dev = Fase("Fase de Desarrollo")
        tarea_backend = Tarea("API REST Login", costo_base=200.0, horas=10)
        fase_dev.agregar_elemento(tarea_backend)
        proyecto.agregar_fase(fase_dev)

        print(f"\nCosto inicial (Por Horas): ${proyecto.get_costo():.2f}")
        
        # Cambio dinámico de Strategy
        proyecto.set_estrategia(CostoPorPuntosFuncion(valor_punto=150.0))
        print(f"Nuevo costo (Puntos de Función): ${proyecto.get_costo():.2f}\n")

        # Cambiar estado e invocar Observer
        tarea_backend.cambiar_estado("Completado", proyecto)

        # 3. Decorator & Personal
        print("\n--- GESTIÓN DE PERSONAL ---")
        emp = EmpleadoBase("E-101", "Carlos Pérez", salario_base=2500.0)
        print(f"Empleado base: {emp.nombre} | Salario: ${emp.get_salario()} | Permisos: {emp.get_permisos()}")

        # Encadenamiento dinámico de responsabilidades
        emp_decorado = LiderTecnicoDecorator(emp)
        emp_decorado = SoporteFinDeSemanaDecorator(emp_decorado)
        print(f"Empleado con responsabilidades: {emp.nombre} | Salario: ${emp_decorado.get_salario()} | Permisos: {emp_decorado.get_permisos()}")

        # 4. Pipeline de Pruebas
        print("\n--- PIPELINE DE PRUEBAS ---")
        fabrica = FabricaWeb()
        paquete = fabrica.crear_paquete()

        p1 = AnalisisEstatico()
        p2 = PruebasUnitarias()
        p3 = PruebasIntegracion()
        p4 = PruebasSeguridad()

        p1.set_siguiente(p2).set_siguiente(p3).set_siguiente(p4)
        print(f"Ejecutando pipeline para tecnología: {paquete.tecnologia}")
        p1.ejecutar_pipeline(paquete)

        # 5. Command, Mediator y Adapter
        print("\n--- CONTROL DE CAMBIOS Y CALENDARIO ---")
        self.calendario.agendar_reunion("2026-10-05 10:00 AM", "Revisión de Cambios")
        self.mediador.notificar(self, "ActaRegistrada")

        cmd = ModificarRequerimientoCommand(proyecto, "Agregar Autenticación de 2 Factores")
        self.invocador.ejecutar_orden(cmd)
        self.invocador.deshacer_ultimo()


if __name__ == "__main__":
    facade = DevEnterpriseOSFacade()
    facade.demo_sistema()