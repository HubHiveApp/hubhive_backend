from sqlalchemy.sql import func
from app.extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    amount    = db.Column(db.Numeric(10, 2), nullable=False)
    currency  = db.Column(db.String(3), default="USD")
    status    = db.Column(db.String(50), default="pending")  # pending|completed|failed
    payment_method = db.Column(db.String(100))
    stripe_payment_intent_id = db.Column(db.String(255))
    description = db.Column(db.Text)
    metadata    = db.Column(db.JSON)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    user = db.relationship("User", backref="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
