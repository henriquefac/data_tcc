import os
from dataclasses import dataclass, field
from threading import Lock
from typing import ClassVar, TypeVar, Type, Callable, Any
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- Funções Utilitárias ---

def _get_required_env(key: str) -> str:
    """Busca uma variável de ambiente e levanta um erro se não for encontrada."""
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(
            f"Variável de ambiente obrigatória '{key}' não encontrada. "
            "Verifique seu arquivo '.env' ou as variáveis do sistema."
        )
    return value

def _get_optional_env(key: str, default: Any) -> Any:
    """Busca uma variável de ambiente, retornando um default se não for encontrada."""
    return os.getenv(key, default)

# --- Classes de Domínio ---

@dataclass(frozen=True) # frozen=True garante imutabilidade após a criação
class ENVDomain:
    """Classe base abstrata para domínios de variáveis de ambiente."""
    pass

@dataclass(frozen=True)
class HuggingFaceEnv(ENVDomain):
    """Domínio para variáveis de ambiente relacionadas ao HuggingFace."""
    HF_TOKEN: str
    HF_MODEL_CACHE: str

# --- Mapeamento de Domínios ---

# Função para carregar as variáveis do domínio HuggingFaceEnv
def load_huggingface_env() -> HuggingFaceEnv:
    return HuggingFaceEnv(
        HF_TOKEN=_get_required_env("HF_TOKEN"),
        # Exemplo de variável opcional com conversão de tipo implícita
        HF_MODEL_CACHE=_get_optional_env("HF_MODEL_CACHE", "cache_dir"),
    )

# Tipo genérico para as classes de domínio
D = TypeVar('D', bound=ENVDomain)

# Dicionário de mapeamento: Onde a chave é a CLASSE e o valor é a FUNÇÃO DE CARREGAMENTO.
DOMAIN_LOADERS: dict[Type[ENVDomain], Callable[[], ENVDomain]] = {
    HuggingFaceEnv: load_huggingface_env,
    # Adicione novos domínios aqui para torná-los acessíveis
}


# --- Manager Singleton ---

class EnvManager:
    """
    Singleton central para gerenciar e fornecer acesso aos domínios de variáveis.
    """
    _instance: ClassVar["EnvManager|None"] = None
    _lock: ClassVar[Lock] = Lock()
    _domains: dict[Type[ENVDomain], ENVDomain]

    def __new__(cls, *args, **kwargs) -> "EnvManager":
        """Implementa o padrão Singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Cria a instância
                    cls._instance = super().__new__(cls)
                    # Inicializa o dicionário para armazenar as instâncias de domínio
                    cls._instance._domains = {}
        return cls._instance

    def _get_domain_instance(self, domain_class: Type[D]) -> D:
        """Carrega e armazena uma instância de domínio (Lazy Loading)."""
        if domain_class not in self._domains:
            # 1. Verifica se a classe de domínio está mapeada no DOMAIN_LOADERS
            if domain_class not in DOMAIN_LOADERS:
                raise ValueError(f"Domínio '{domain_class.__name__}' não mapeado no DOMAIN_LOADERS.")

            # 2. Executa a função de carregamento e armazena o resultado
            loader_func = DOMAIN_LOADERS[domain_class]
            # A chamada do loader_func executa a busca no os.getenv()
            self._domains[domain_class] = loader_func()

        # 3. Retorna a instância armazenada
        return self._domains[domain_class] # type: ignore

    # --- Métodos de Acesso (Facilitadores) ---

    def huggingface(self) -> HuggingFaceEnv:
        """Acesso facilitado ao domínio HuggingFaceEnv."""
        return self._get_domain_instance(HuggingFaceEnv)


    # --- Método Genérico (para customização) ---

    def get_domain(self, domain_class: Type[D]) -> D:
        """Acesso genérico a qualquer domínio configurado."""
        return self._get_domain_instance(domain_class)
