from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

import src.crud.workout as workout_service
import src.crud.workout_exercise as workout_exercise_service
from src.schemas.workout import Workout, WorkoutBase, WorkoutCreate, WorkoutUpdate
from src.schemas.workout_exercise import WorkoutExercise
from src.models.user import User as UserDB
from src.core.dependencies import get_db, get_current_user

router = APIRouter(prefix="/workouts", tags=["Workout"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WorkoutBase)
def create_workout(current_user: Annotated[UserDB, Depends(get_current_user)],
                   workout_base: WorkoutBase, db: Session = Depends(get_db)):
    # plans = plan_service.get_plans_by_user_id(db, current_user.id)
    # if workout_base.plan_id is not None and not (workout_base.plan_id not in [plan_id for plan_id in plans]):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You do not have access to a plan that you try to assign workout to."
    #     )
    workout = WorkoutCreate(**workout_base.model_dump(), user_id=current_user.id)
    return workout_service.create_workout(db, workout)


@router.get("/{workout_id}", response_model=Workout)
def get_workout(workout_id: int, current_user: Annotated[UserDB, Depends(get_current_user)]):
    workout = next((wo for wo in current_user.workouts if workout_id == wo.id), None)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout


@router.get("/{workout_id}/workout_exercises", response_model=list[WorkoutExercise])
def get_workout_exercises_in_workout(workout_id: int, current_user: Annotated[UserDB, Depends(get_current_user)],
                                     db: Session = Depends(get_db)):
    workouts = workout_service.get_workouts_by_user_id(db, current_user.id)
    workout = next((wo for wo in workouts if workout_id == wo.id), None)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout_exercise_service.get_workout_exercises_by_workout_id(db, workout_id)


@router.get("", response_model=list[Workout])
def get_workouts(current_user: Annotated[UserDB, Depends(get_current_user)], db: Session = Depends(get_db)):
    return workout_service.get_workouts_by_user_id(db, current_user.id)


@router.patch("", response_model=Workout)
def update_workout(current_user: Annotated[UserDB, Depends(get_current_user)],
                   workout_input: WorkoutUpdate,
                   db: Session = Depends(get_db)):
    workouts = workout_service.get_workouts_by_user_id(db, current_user.id)
    db_workout = next((wo for wo in workouts if wo.id == workout_input.id), None)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    model_workout = Workout(**db_workout.__dict__)
    update_data = workout_input.dict(exclude_unset=True)
    updated_workout = model_workout.model_copy(update=update_data)
    return workout_service.update_workout(db, updated_workout)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, current_user: Annotated[UserDB, Depends(get_current_user)],
                   db: Session = Depends(get_db)):
    workouts = workout_service.get_workouts_by_user_id(db, current_user.id)
    workout = next((tr for tr in workouts if tr.id == workout_id), None)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    workout_service.delete_workout(db, workout_id)