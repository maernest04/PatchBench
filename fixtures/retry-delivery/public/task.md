# Implement reliable delivery

Implement `DeliveryService.deliver` so a first delivery records an event and returns `True`. A retried delivery with the same `message_id` must not record a duplicate event and must return `False`.
