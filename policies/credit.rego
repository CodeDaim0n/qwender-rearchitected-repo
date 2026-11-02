package credit
import rego.v1

bit(b) := 1 if b
else := 0

band(m, t) := 3 if m >= t[12]
else := 2 if m >= t[11]
else := 1 if m >= t[10]
else := 0

outcome(ts) := 0 if { some i in [0,1]; ts[i] == 1 }
else := 1 if { some i in [2,3,4]; ts[i] == 1 }
else := 2 if { some i in [5,6,7,8]; ts[i] == 1 }
else := 3 if { some i in [9,10,11,12,13]; ts[i] == 1 }
else := 4

is_reason(i, o) if { o == 0; i < 2 }
is_reason(i, o) if { o == 1; i >= 2; i < 5 }
is_reason(i, o) if { o in [2,3]; i >= 5; i < 14 }
is_reason(i, o) if { o == 4; i == 14 }
all_true(bs) := count([v | some v in bs; v == true]) == count(bs)
reason_bit(i,o,t) := 1 if { t == 1; is_reason(i,o) }
else := 0

assess(row) := result if {
    c := row.calculations
    f := row.flags
    t := input.thresholds
    b := band(row.margin, t)
    severe := c[5] >= t[7]
    many := c[3] >= t[8]
    repeat := c[4] == 1
    severity := c[5] >= t[6]
    repeated := count([v | some v in [severe, many]; v]) > 0
    soft_repeat := count([v | some v in [repeat, severity]; v]) > 0
    high := c[1] >= t[2]
    low := all_true([c[11] > 0, c[6] < t[4]])
    rising := c[7] >= t[5]
    soft_count := sum([bit(soft_repeat), bit(high), bit(low), bit(rising)])
    ts := [f[0], f[1], bit(repeated), bit(all_true([c[10] == 1, c[1] >= t[0]])),
           bit(all_true([c[1] >= t[3], c[3] >= 1])), f[3], f[2], bit(b == 3),
           bit(soft_count >= t[9]), bit(soft_repeat), bit(high), bit(low), bit(rising), bit(b == 2), 0]
    o := outcome(ts)
    triggers := array.concat(array.slice(ts,0,14), [bit(o == 4)])
    reasons := [reason_bit(i,o,triggers[i]) | some i in numbers.range(0,14)]
    result := {"risk_band": b, "outcome": o, "triggers": triggers, "final_reasons": reasons}
}

decisions := [assess(row) | some row in input.rows]
