"""
CRUD Base genérico usando Repository Pattern
"""
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from ..core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD base genérico com operações padrão:
    - Create
    - Read (get, get_multi)
    - Update
    - Delete

    Exemplo de uso:
        class CRUDJogador(CRUDBase[Jogador, JogadorCreate, JogadorUpdate]):
            pass

        jogador_crud = CRUDJogador(Jogador)
    """

    def __init__(self, model: Type[ModelType]):
        """
        Inicializa CRUD com o model SQLAlchemy.

        Args:
            model: Classe do model SQLAlchemy
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Busca um registro por ID.

        Args:
            db: Sessão do banco
            id: ID do registro

        Returns:
            Instância do model ou None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Busca múltiplos registros com paginação.

        Args:
            db: Sessão do banco
            skip: Número de registros para pular
            limit: Número máximo de registros

        Returns:
            Lista de instâncias do model
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Cria um novo registro.

        Args:
            db: Sessão do banco
            obj_in: Schema Pydantic com dados de criação

        Returns:
            Instância do model criada
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Atualiza um registro existente.

        Args:
            db: Sessão do banco
            db_obj: Instância do model a ser atualizada
            obj_in: Schema Pydantic ou dict com dados de atualização

        Returns:
            Instância do model atualizada
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ModelType:
        """
        Deleta um registro por ID.

        Args:
            db: Sessão do banco
            id: ID do registro

        Returns:
            Instância do model deletada
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """
        Conta total de registros.

        Args:
            db: Sessão do banco

        Returns:
            Número total de registros
        """
        return db.query(self.model).count()

    def exists(self, db: Session, id: int) -> bool:
        """
        Verifica se um registro existe.

        Args:
            db: Sessão do banco
            id: ID do registro

        Returns:
            True se existe, False caso contrário
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None
