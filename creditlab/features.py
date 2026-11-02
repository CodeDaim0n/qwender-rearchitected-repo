"""Independent feature calculations. No decisions, language model or network calls."""
import numpy as np


def calculate(x, missing, bounds, thresholds):
    x = np.asarray(x, dtype=np.int64)
    missing = np.asarray(missing, dtype=bool)
    limit = np.maximum(x[:, 0], 1)
    statuses, bills, payments = x[:, 5:11], x[:, 11:17], x[:, 17:23]
    positive = np.maximum(bills, 0)
    bill_total, payment_total = positive.sum(1), payments.sum(1)
    scale = thresholds[0]
    current = positive[:, 0] * scale // limit
    count = (statuses > 0).sum(1)
    def mad(v):
        n = v.shape[1]
        return np.abs(v * n - v.sum(1)[:, None]).sum(1) // (n*n)
    calculations = np.column_stack([
        current, positive.max(1) * scale // limit, bill_total * scale // (6*limit),
        count, count >= 2, np.maximum(statuses.max(1), 0),
        payment_total * scale // np.maximum(bill_total, 1),
        (bills[:, 0]-bills[:, 5]) * scale // limit, mad(bills), mad(payments),
        (payment_total == 0) & (current >= thresholds[1]), bill_total, payment_total,
    ]).astype(np.int64)
    flags = np.column_stack([
        missing.any(1),
        (x[:, 0] <= 0) | (x[:, 4] < 0) | (x[:, 4] > 120) |
        (statuses < -2).any(1) | (statuses > 9).any(1) | (payments < 0).any(1),
        ((x < bounds[0]) | (x > bounds[1])).any(1),
        ~np.isin(x[:, 1], [1,2]) | ~np.isin(x[:, 2], [1,2,3,4]) | ~np.isin(x[:, 3], [1,2,3]),
        np.isin(statuses, [-2,0]).any(1), np.zeros(len(x), dtype=bool),
    ]).astype(np.int64)
    return calculations, flags
