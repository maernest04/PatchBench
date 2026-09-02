# Retry failed operations

Implement `RetryRunner.run`. It receives an `operation` callable, a maximum number of attempts, and a backoff in seconds. Retry after `ValueError` failures until the operation returns a result or all attempts are used. Return the successful result.
