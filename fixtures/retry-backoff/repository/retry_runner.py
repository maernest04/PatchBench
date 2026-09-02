class RetryRunner:
    def __init__(self, sleep):
        self.sleep = sleep

    def run(self, operation, attempts, backoff_seconds):
        raise NotImplementedError
