'' effects/plasma.bi — classic four-wave plasma
#pragma once

Sub Effect_Plasma(t As Single)
    For y As Integer = 0 To DEMO_H - 1
        Dim row As ULong Ptr = demoPixels + y * demoStride
        For x As Integer = 0 To DEMO_W - 1
            Dim v As Single = _
                SSIN(CInt(x * 8       + t * 200) And LUT_MASK) + _
                SSIN(CInt(y * 6       + t * 150) And LUT_MASK) + _
                SSIN(CInt((x + y) * 5 + t * 100) And LUT_MASK) + _
                SSIN(CInt(Sqr(Single((x - DEMO_W \ 2) ^ 2 + (y - DEMO_H \ 2) ^ 2)) * 7 + t * 175) And LUT_MASK)

            Dim p As Integer = CInt(v * 512) And LUT_MASK
            row[x] = RGB( _
                CInt((SSIN(p)                                    + 1.0) * 127), _
                CInt((SSIN((p + LUT_SIZE \ 3)     And LUT_MASK) + 1.0) * 127), _
                CInt((SSIN((p + LUT_SIZE * 2 \ 3) And LUT_MASK) + 1.0) * 127))
        Next x
    Next y
End Sub
