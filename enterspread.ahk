#Requires AutoHotkey v2.0
#SingleInstance Force

SetWorkingDir("C:\Users\Administrator\Desktop\spreadchart")
CoordMode("Mouse", "Screen")

Sleep(10000)
MouseClick("Left", 35, 232)
Sleep(5000)

MouseClick("Left", 276, 144)
Sleep(1000)

Send("^a")

SendText("1*CLF24-2*CLG24+1*CLH24-1*CLV24+2*CLX24-1*CLZ24")
Sleep(1000)

; Sleep(500000)


MouseClick("Left", 538, 147)
Sleep(2000)

MouseClick("Left", 524, 187)
Sleep(2000)

MouseClick("Left", 528, 210)
Sleep(2000)

MouseClick("Left", 763, 148)
Sleep(2000)

MouseClick("Left", 1880, 570)
Sleep(2000)
