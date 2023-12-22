from dateutil.relativedelta import relativedelta
from psqlextra.partitioning import (
    PostgresPartitioningManager,
    PostgresCurrentTimePartitioningStrategy,
    PostgresTimePartitionSize,
)
from psqlextra.partitioning.config import PostgresPartitioningConfig

from db.models import Attendance

# python manage.py pgmakemigrations
# python manage.py pgpartition
manager = PostgresPartitioningManager([
    PostgresPartitioningConfig(
        model=Attendance,
        strategy=PostgresCurrentTimePartitioningStrategy(
            size=PostgresTimePartitionSize(years=1),
            count=10,
            max_age=relativedelta(
                years=20
            ),
        ),
    ),
])
