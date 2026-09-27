#!/usr/bin/env python3
"""
Offline VBA Generator — zero cost, zero internet, no AI model involved.

Same philosophy as offline_prompt_generator.py: hardcoded templates and
string logic only (Python standard library, no dependencies). Answers your
questions, fills in a known-good VBA skeleton for common Excel/reconciliation
automation tasks, and prints ready-to-paste code.

Usage:
    python3 vba_generator.py

To use the generated code: open Excel, press Alt+F11 (Windows) or
Option+F11 (Mac) to open the VBA editor, insert a new Module
(Insert > Module), and paste the code in. Run it from Excel via
Developer tab > Macros, or assign it to a button (see the note printed
after each macro).
"""

import sys

DIVIDER = "-" * 60


def ask(question, default=None):
    suffix = f" [{default}]" if default else ""
    answer = input(f"{question}{suffix}: ").strip()
    return answer if answer else (default or "")


def ask_yes_no(question, default_yes=True):
    suffix = " [Y/n]" if default_yes else " [y/N]"
    answer = input(f"{question}{suffix}: ").strip().lower()
    if not answer:
        return default_yes
    return answer.startswith("y")


HOW_TO_RUN = (
    "\nHOW TO USE THIS:\n"
    "1. Open Excel. Press Alt+F11 (Windows) or Option+F11 (Mac) for the VBA editor.\n"
    "2. Insert > Module, then paste the code in.\n"
    "3. Save the workbook as .xlsm (macro-enabled) if it isn't already.\n"
    "4. Run it: Developer tab > Macros > select the Sub name > Run.\n"
    "   (Optional) Add a button: Developer tab > Insert > Button (Form Control),\n"
    "   draw it on the sheet, and assign this macro to it.\n"
)


# ---------------------------------------------------------------------------
# Category builders. Each asks its own fill-in questions and returns
# (sub_name, vba_code_string).
# ---------------------------------------------------------------------------

def build_compare_columns():
    sheet_a = ask("Sheet name for the first (internal) data set", "Internal")
    sheet_b = ask("Sheet name for the second (external/custodian) data set", "External")
    key_col = ask("Column letter holding the matching key (trade ID, account #, etc.) in both sheets", "A")
    value_col = ask("Column letter holding the value to compare (amount, quantity, etc.)", "B")
    tolerance = ask("Acceptable difference before flagging a break (0 for exact match)", "0")
    output_sheet = ask("Sheet name to write the break report to (created if missing)", "Breaks")

    code = f'''Option Explicit

' Compares {sheet_a}!{key_col}:{value_col} against {sheet_b}!{key_col}:{value_col} by matching key,
' and lists any row where the values differ by more than the tolerance.
Sub CompareAndFlagBreaks()
    Dim wsA As Worksheet, wsB As Worksheet, wsOut As Worksheet
    Dim lastRowA As Long, lastRowB As Long, i As Long, j As Long
    Dim outRow As Long
    Dim tolerance As Double
    Dim keyA As Variant, valA As Double, valB As Variant, found As Boolean

    tolerance = {tolerance}

    Set wsA = ThisWorkbook.Sheets("{sheet_a}")
    Set wsB = ThisWorkbook.Sheets("{sheet_b}")

    ' Create (or clear) the output sheet
    On Error Resume Next
    Set wsOut = ThisWorkbook.Sheets("{output_sheet}")
    On Error GoTo 0
    If wsOut Is Nothing Then
        Set wsOut = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsOut.Name = "{output_sheet}"
    Else
        wsOut.Cells.Clear
    End If

    wsOut.Range("A1").Value = "Key"
    wsOut.Range("B1").Value = "{sheet_a} Value"
    wsOut.Range("C1").Value = "{sheet_b} Value"
    wsOut.Range("D1").Value = "Difference"
    outRow = 2

    lastRowA = wsA.Cells(wsA.Rows.Count, "{key_col}").End(xlUp).Row
    lastRowB = wsB.Cells(wsB.Rows.Count, "{key_col}").End(xlUp).Row

    For i = 2 To lastRowA
        keyA = wsA.Cells(i, "{key_col}").Value
        If keyA <> "" Then
            found = False
            For j = 2 To lastRowB
                If wsB.Cells(j, "{key_col}").Value = keyA Then
                    found = True
                    valA = wsA.Cells(i, "{value_col}").Value
                    valB = wsB.Cells(j, "{value_col}").Value
                    If Abs(valA - valB) > tolerance Then
                        wsOut.Cells(outRow, 1).Value = keyA
                        wsOut.Cells(outRow, 2).Value = valA
                        wsOut.Cells(outRow, 3).Value = valB
                        wsOut.Cells(outRow, 4).Value = valA - valB
                        outRow = outRow + 1
                    End If
                    Exit For
                End If
            Next j
            If Not found Then
                wsOut.Cells(outRow, 1).Value = keyA
                wsOut.Cells(outRow, 2).Value = wsA.Cells(i, "{value_col}").Value
                wsOut.Cells(outRow, 3).Value = "MISSING in {sheet_b}"
                wsOut.Cells(outRow, 4).Value = ""
                outRow = outRow + 1
            End If
        End If
    Next i

    wsOut.Columns("A:D").AutoFit
    MsgBox (outRow - 2) & " break(s) found. See the '" & "{output_sheet}" & "' sheet.", vbInformation
End Sub
'''
    return "CompareAndFlagBreaks", code


def build_highlight_duplicates():
    sheet = ask("Sheet name", "Sheet1")
    col = ask("Column letter to check for duplicates", "A")
    color = ask("Highlight color (name: red/yellow/green/orange)", "yellow")
    color_map = {"red": "255, 199, 199", "yellow": "255, 242, 150", "green": "198, 239, 206", "orange": "252, 213, 180"}
    rgb = color_map.get(color.lower(), color_map["yellow"])

    code = f'''Option Explicit

' Highlights every duplicate value in {sheet}!{col} (keeps the first occurrence
' unhighlighted, flags every repeat).
Sub HighlightDuplicates()
    Dim ws As Worksheet
    Dim lastRow As Long, i As Long, j As Long
    Dim seen As Object

    Set ws = ThisWorkbook.Sheets("{sheet}")
    Set seen = CreateObject("Scripting.Dictionary")

    lastRow = ws.Cells(ws.Rows.Count, "{col}").End(xlUp).Row

    For i = 2 To lastRow
        Dim v As Variant
        v = ws.Cells(i, "{col}").Value
        If v <> "" Then
            If seen.Exists(v) Then
                ws.Cells(i, "{col}").Interior.Color = RGB({rgb})
                ws.Cells(seen(v), "{col}").Interior.Color = RGB({rgb})
            Else
                seen.Add v, i
            End If
        End If
    Next i

    MsgBox "Duplicate check complete.", vbInformation
End Sub
'''
    return "HighlightDuplicates", code


def build_data_cleaning():
    sheet = ask("Sheet name", "Sheet1")
    col_range = ask("Column range to clean (e.g. A:D)", "A:D")

    code = f'''Option Explicit

' Trims whitespace and removes fully-blank rows within {sheet}!{col_range}.
Sub CleanData()
    Dim ws As Worksheet
    Dim lastRow As Long, lastCol As Long, r As Long, c As Long
    Dim isBlankRow As Boolean

    Set ws = ThisWorkbook.Sheets("{sheet}")
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    ' Trim whitespace in every cell of the range
    Dim rng As Range
    Set rng = ws.Range("{col_range}1:{col_range}").Resize(lastRow)
    For r = 1 To rng.Rows.Count
        For c = 1 To rng.Columns.Count
            If VarType(rng.Cells(r, c).Value) = vbString Then
                rng.Cells(r, c).Value = Trim(rng.Cells(r, c).Value)
            End If
        Next c
    Next r

    ' Remove fully-blank rows, bottom-up so row indices don't shift
    For r = lastRow To 2 Step -1
        isBlankRow = True
        For c = 1 To rng.Columns.Count
            If Trim(CStr(rng.Cells(r - rng.Row + 1, c).Value)) <> "" Then
                isBlankRow = False
                Exit For
            End If
        Next c
        If isBlankRow Then ws.Rows(r).Delete
    Next r

    MsgBox "Cleanup complete.", vbInformation
End Sub
'''
    return "CleanData", code


def build_conditional_export():
    sheet = ask("Sheet name to export from", "Sheet1")
    col_range = ask("Range to export (e.g. A1:F50, or leave blank for used range)", "")
    range_expr = f'"{col_range}"' if col_range else "Nothing"

    code = f'''Option Explicit

' Exports {sheet} (or a specific range) to a CSV file next to the workbook.
Sub ExportRangeToCSV()
    Dim ws As Worksheet
    Dim exportRange As Range
    Dim outPath As String

    Set ws = ThisWorkbook.Sheets("{sheet}")
    If {range_expr} Is Nothing Then
        Set exportRange = ws.UsedRange
    Else
        Set exportRange = ws.Range({range_expr})
    End If

    outPath = ThisWorkbook.Path & Application.PathSeparator & "{sheet}_export_" & _
        Format(Now, "yyyymmdd_hhnnss") & ".csv"

    Dim wsCopy As Workbook
    Set wsCopy = Workbooks.Add
    exportRange.Copy
    wsCopy.Sheets(1).Range("A1").PasteSpecial xlPasteValues
    Application.CutCopyMode = False
    wsCopy.SaveAs Filename:=outPath, FileFormat:=xlCSV
    wsCopy.Close SaveChanges:=False

    MsgBox "Exported to: " & outPath, vbInformation
End Sub
'''
    return "ExportRangeToCSV", code


def build_summary_report():
    sheet = ask("Sheet name with the raw data", "Sheet1")
    group_col = ask("Column letter to group by (e.g. category, break type)", "A")
    sum_col = ask("Column letter to sum per group", "B")
    output_sheet = ask("Sheet name for the summary (created if missing)", "Summary")

    code = f'''Option Explicit

' Groups {sheet}!{group_col} and sums {sheet}!{sum_col} per group, writing
' the result to {output_sheet}.
Sub BuildSummaryReport()
    Dim wsIn As Worksheet, wsOut As Worksheet
    Dim lastRow As Long, i As Long, outRow As Long
    Dim totals As Object
    Dim key As Variant

    Set wsIn = ThisWorkbook.Sheets("{sheet}")
    Set totals = CreateObject("Scripting.Dictionary")

    lastRow = wsIn.Cells(wsIn.Rows.Count, "{group_col}").End(xlUp).Row

    For i = 2 To lastRow
        key = wsIn.Cells(i, "{group_col}").Value
        If key <> "" Then
            If totals.Exists(key) Then
                totals(key) = totals(key) + wsIn.Cells(i, "{sum_col}").Value
            Else
                totals.Add key, wsIn.Cells(i, "{sum_col}").Value
            End If
        End If
    Next i

    On Error Resume Next
    Set wsOut = ThisWorkbook.Sheets("{output_sheet}")
    On Error GoTo 0
    If wsOut Is Nothing Then
        Set wsOut = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsOut.Name = "{output_sheet}"
    Else
        wsOut.Cells.Clear
    End If

    wsOut.Range("A1").Value = "Group"
    wsOut.Range("B1").Value = "Total"
    outRow = 2
    For Each key In totals.Keys
        wsOut.Cells(outRow, 1).Value = key
        wsOut.Cells(outRow, 2).Value = totals(key)
        outRow = outRow + 1
    Next key

    wsOut.Columns("A:B").AutoFit
    MsgBox "Summary built on '" & "{output_sheet}" & "'.", vbInformation
End Sub
'''
    return "BuildSummaryReport", code


def build_general():
    task_desc = ask("Describe what the macro should do, in your own words")
    sheet = ask("Main sheet it should work on", "Sheet1")

    code = f'''Option Explicit

' TODO: {task_desc}
' Starting skeleton — fill in the logic below. This gives you Option Explicit,
' a worksheet reference, and a message box confirmation so you have a working
' shell to build from rather than a blank module.
Sub CustomMacro()
    Dim ws As Worksheet
    Dim lastRow As Long, i As Long

    Set ws = ThisWorkbook.Sheets("{sheet}")
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    For i = 2 To lastRow
        ' TODO: your row-by-row logic here, e.g.:
        ' If ws.Cells(i, "A").Value = "something" Then
        '     ws.Cells(i, "B").Value = "flagged"
        ' End If
    Next i

    MsgBox "Done.", vbInformation
End Sub
'''
    return "CustomMacro", code


CATEGORIES = {
    "1": ("Compare two ranges / flag mismatches (reconciliation break-finder)", build_compare_columns),
    "2": ("Highlight duplicate values in a column", build_highlight_duplicates),
    "3": ("Data cleaning (trim whitespace, remove blank rows)", build_data_cleaning),
    "4": ("Export a range to CSV", build_conditional_export),
    "5": ("Build a group-by summary report", build_summary_report),
    "6": ("General / anything else (skeleton macro)", build_general),
}


def main():
    print(DIVIDER)
    print("OFFLINE VBA GENERATOR — no internet, no API, no tokens, no AI model.")
    print(DIVIDER)
    print("Pick a category:")
    for key, (label, _) in CATEGORIES.items():
        print(f"  {key}. {label}")
    print(DIVIDER)
    choice = ask("Category number", "6")
    _, builder = CATEGORIES.get(choice, CATEGORIES["6"])
    print(DIVIDER)

    sub_name, code = builder()

    print("\n" + DIVIDER)
    print(f"GENERATED VBA MACRO: {sub_name}")
    print(DIVIDER)
    print(code)
    print(HOW_TO_RUN)
    print(DIVIDER)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
