import sys
BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/seto"
f=BASE+"/m-2.xls"
try:
    import xlrd
except Exception as e:
    print("NO_XLRD", e); sys.exit(2)
wb=xlrd.open_workbook(f)
for sh in wb.sheets():
    print("=== SHEET:", sh.name, sh.nrows, sh.ncols)
    for r in range(sh.nrows):
        row=[]
        for c in range(sh.ncols):
            v=sh.cell_value(r,c)
            if isinstance(v,float) and v==int(v): v=int(v)
            row.append(str(v))
        print(r, "|".join(row))
