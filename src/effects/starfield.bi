'' effects/starfield.bi — 3D starfield
#pragma once

Const NUM_STARS As Integer = 400

Type Star
    x As Single
    y As Single
    z As Single
End Type

Dim Shared stars(NUM_STARS - 1) As Star

Sub Effect_Starfield_Init()
    Randomize
    For i As Integer = 0 To NUM_STARS - 1
        stars(i).x = (Rnd - 0.5) * 2.0
        stars(i).y = (Rnd - 0.5) * 2.0
        stars(i).z = Rnd
    Next i
End Sub

Sub Effect_Starfield(dt As Single)
    ' Clear to black
    For i As Long = 0 To DEMO_W * DEMO_H - 1
        demoPixels[i] = RGB(0, 0, 0)
    Next i

    Const CX As Integer = DEMO_W \ 2
    Const CY As Integer = DEMO_H \ 2
    Const SPEED As Single = 0.4

    For i As Integer = 0 To NUM_STARS - 1
        stars(i).z -= dt * SPEED
        If stars(i).z <= 0 Then
            stars(i).x = (Rnd - 0.5) * 2.0
            stars(i).y = (Rnd - 0.5) * 2.0
            stars(i).z = 1.0
        End If

        Dim sx As Integer = CInt(CX + stars(i).x / stars(i).z * CX)
        Dim sy As Integer = CInt(CY + stars(i).y / stars(i).z * CY)

        If sx >= 0 And sx < DEMO_W And sy >= 0 And sy < DEMO_H Then
            Dim bright As Integer = CInt((1.0 - stars(i).z) * 255)
            PIXEL(sx, sy) = RGB(bright, bright, bright)
        End If
    Next i
End Sub
