from enum import Enum


class InfoMessageStatuses(Enum):
    RECEIVED = 1
    WAITING_PROCESSING = 2
    IN_PROCESSING = 3
    ONHOLD = 4.1


class PaymentStatuses(Enum):
    READY_FOR_PROCESSING = 'Ready for processing'
    SUBMITTED = 'Submitted'
    SUCCESSFULLY_PAID = 'Successfully paid'
    DENIED = 'Denied payment'
    PROCESSED_BY_BANK = 'Processed Bank'


CI_NODE_PORT_IP = '10.129.71.49'
