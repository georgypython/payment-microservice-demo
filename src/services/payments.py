from sqlalchemy.ext.asyncio import AsyncSession


class PaymentsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
