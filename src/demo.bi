'' demo.bi — shared screen, buffer, and sine LUT
#pragma once

#include "fbgfx.bi"
Using FB

Const DEMO_W     As Integer = 320
Const DEMO_H     As Integer = 200
Const DEMO_SCALE As Integer = 2
Const DEMO_FPS   As Integer = 60

Const LUT_SIZE   As Integer = 4096
Const LUT_MASK   As Integer = LUT_SIZE - 1

Dim Shared sinLut(LUT_MASK) As Single

Dim Shared demoBuf    As Any Ptr
Dim Shared demoPixels As ULong Ptr
Dim Shared demoStride As Long

Sub DemoInit()
    For i As Integer = 0 To LUT_MASK
        sinLut(i) = Sin(i * 6.283185307 / LUT_SIZE)
    Next i

    ScreenRes DEMO_W * DEMO_SCALE, DEMO_H * DEMO_SCALE, 32, 2
    ScreenSet 1, 0
    WindowTitle "Demo"
    Cursor Off

    Dim bPitch As Long
    demoBuf = ImageCreate(DEMO_W, DEMO_H, 0, 32)
    ImageInfo demoBuf, , , , bPitch, demoPixels
    demoStride = bPitch \ SizeOf(ULong)
End Sub

Sub DemoFlip()
    ScreenLock
    Put (0, 0)-(DEMO_W * DEMO_SCALE - 1, DEMO_H * DEMO_SCALE - 1), demoBuf, Stretch
    ScreenUnlock
    ScreenCopy
End Sub

Sub DemoShutdown()
    ImageDestroy demoBuf
End Sub

'' Inline helpers
#define SSIN(x)  sinLut((x) And LUT_MASK)
#define PIXEL(x, y) demoPixels((y) * demoStride + (x))
