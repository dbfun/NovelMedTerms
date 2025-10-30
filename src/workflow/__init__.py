"""Схема workflow.yaml для типизации"""
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, model_validator


class Experiment(BaseModel):
    description: str = Field(..., description="Описание эксперимента")


class Module(BaseModel, extra="allow"):
    module: str = Field(..., description="Название модуля")
    type: str = Field(..., description="Тип модуля (конкретная реализация)")
    params: Optional[Dict[str, Any]] = None


class Stage(BaseModel):
    name: str = Field(..., description="Название этапа")
    modules: List[Module]


class Config(BaseModel):
    experiment: Experiment
    stages: List[Stage]
