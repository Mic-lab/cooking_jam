import math

class Timer:

    def __init__(self, duration, done=False):
        self.duration = duration

        if not done:
            self.reset()
        else:
            self.frame = self.duration
            self.done = True

    def reset(self):
        self.frame = 0
        self.done = False

    def update(self):
        if not self.done:
            self.frame += 1
        self.done = self.frame == self.duration

    def get_ease_in_out_sin(self):
        x = self.ratio
        return -(math.cos((math.pi*x)) - 1) / 2


    def get_ease_squared(self):
        # return 1 - (1 - self.frame) ** 2
        return 1 - (1 - self.ratio) ** 2

    C4 = (2 * math.pi) / 3;
    def easeOutElastic(self):
        x = self.ratio
        if x in (0, 1): return x
        return (2 ** (-10 * x)) * math.sin((x * 10 - 0.75) * self.C4) + 1


    @property
    def ratio(self):
        return self.frame / self.duration

    def __repr__(self):
        return f'<Timer({self.frame}/{self.duration})>'

    @staticmethod
    def update_timers(timers):
        new_timers = []
        for timer in timers:
            if not timer.done:
                new_timers.append(timer)
            timer.update()
        return new_timers
