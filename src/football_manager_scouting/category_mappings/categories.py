"""Predefined categories for filtering which attributes and statistics to be displayed in the index and spider."""

STATS = {
    'def': ['aerA', 'hdrsW', 'blk', 'clr', 'tckC', 'presA', 'presC', 'interceptions', 'sprints',  'possLost', 'possWon'],
    'off': ['hdrsW', 'drb', 'opCrsA', 'opCrsC', 'psA', 'psC', 'prPasses', 'opKp', 'chC', 'xa', 'shot', 'sht', 'npXg'],
    'WB':  ['presC', 'interceptions', 'sprints', 'possWon', 'drb', 'opCrsC', 'psC', 'prPasses', 'opKp', 'xa'],
    'BW':  ['aerA', 'hdrsW', 'tckC', 'presA',  'presC', 'interceptions', 'possWon'],
    'DC':  ['hdrsW', 'blk', 'clr', 'tckC', 'interceptions', 'possLost', 'possWon', 'psC', 'prPasses'],
    'DM':  ['hdrsW', 'blk', 'clr', 'tckC', 'presC', 'sprints', 'possWon', 'psC', 'prPasses', 'xa'],
    'MC':  ['presC', 'possWon', 'psC', 'prPasses', 'opKp', 'chC', 'xa'],
    'AM':  ['drb', 'opCrsA', 'opCrsC', 'prPasses', 'opKp', 'xa', 'shot', 'sht', 'npXg'],
    'STC': ['hdrsW', 'tckC', 'presC', 'interceptions', 'psC', 'opKp', 'xa', 'shot', 'sht', 'npXg'],
    'all': ['aerA', 'hdrsW', 'blk', 'clr', 'tckC', 'presA', 'presC', 'interceptions', 'sprints', 'possLost', 'possWon', 'drb', 'opCrsA', 'opCrsC', 'psA', 'psC', 'prPasses', 'opKp', 'chC', 'xa', 'shot', 'sht', 'npXg']
}

ATTRIBUTES = {
    'WB':  ['cro', 'dri', 'fir', 'pas', 'tck', 'tec', 'ant', 'det', 'decisions', 'fla', 'otb', 'pos', 'tea', 'vis', 'wor', 'acc', 'natF', 'pac', 'sta'],
    'DC':  ['hea', 'mar', 'pas', 'tck', 'agg', 'ant', 'bra', 'cmp', 'cnt', 'decisions', 'det', 'pos', 'tea', 'vis', 'wor', 'acc', 'jum', 'natF', 'pac', 'sta', 'str'],
    'DM':  ['fir', 'hea', 'mar', 'pas', 'tck', 'tec', 'agg', 'ant', 'bra', 'cmp', 'cnt', 'decisions', 'det', 'otb', 'pos', 'tea', 'vis', 'wor', 'jum', 'sta', 'str'],
    'MC':  ['dri', 'fir', 'mar', 'pas', 'tck', 'tec', 'ant', 'cmp', 'cnt', 'decisions', 'det', 'fla', 'otb', 'pos', 'tea', 'vis', 'wor', 'acc', 'agi', 'bal', 'natF', 'pac', 'sta'],
    'AM':  ['dri', 'fin', 'fir', 'pas', 'tck', 'tec', 'ant', 'decisions', 'det', 'fla', 'otb', 'tea', 'vis', 'wor', 'acc', 'agi', 'bal', 'natF', 'pac', 'sta',],
    'STC': ['dri', 'fin', 'fir', 'pas',  'tec', 'agg', 'ant', 'bra', 'cmp', 'cnt', 'decisions', 'det', 'fla', 'otb', 'tea', 'vis', 'wor', 'acc', 'agi', 'bal', 'jum', 'natF', 'pac', 'sta', 'str'],
    'all': ['Cor', 'Cro', 'Dri', 'Fin', 'Fir', 'Fre', 'Hea', 'Lon', 'L Th', 'Mar', 'Pas', 'Pen', 'Tck', 'Tec', 'Agg', 'Ant', 'Bra', 'Cmp', 'Cnt', 'Dec', 'Det', 'Fla', 'Ldr', 'OtB', 'Pos', 'Tea', 'Vis', 'Wor', 'Acc', 'Agi', 'Bal', 'Jum', 'NatF', 'Pac', 'Sta', 'Str', 'Aer', 'Cmd', 'Com', 'Ecc', 'Han', 'Kic', '1v1', 'Pun', 'Ref', 'TRO', 'Thr']
}