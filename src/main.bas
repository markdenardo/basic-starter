'' Demoscene template — main.bas
'' Add scenes to the scenes() array; each runs for SCENE_DUR seconds.

#include "demo.bi"
#include "effects/plasma.bi"
#include "effects/starfield.bi"

' ─── Scene table ─────────────────────────────────────────────────────────────

Const SCENE_DUR As Single = 8.0   ' seconds per scene

Type SceneDef
    id As Integer
End Type

Const SCENE_STARFIELD As Integer = 0
Const SCENE_PLASMA    As Integer = 1

Dim scenes(1) As SceneDef
scenes(0).id = SCENE_STARFIELD
scenes(1).id = SCENE_PLASMA

Const NUM_SCENES As Integer = 2

' ─── Init ────────────────────────────────────────────────────────────────────

DemoInit()
Effect_Starfield_Init()

' ─── Timing ──────────────────────────────────────────────────────────────────

Dim tStart  As Double = Timer
Dim tFrame  As Double = Timer
Dim tPrev   As Double = Timer
Dim t       As Single
Dim dt      As Single
Dim scene   As Integer = 0

' ─── Main loop ───────────────────────────────────────────────────────────────

Do
    Dim tNow As Double = Timer
    t  = Single(tNow - tStart)
    dt = Single(tNow - tPrev)
    tPrev = tNow

    ' Advance scene
    Dim sceneT As Single = t - scene * SCENE_DUR
    If sceneT >= SCENE_DUR Then
        scene = (scene + 1) Mod NUM_SCENES
        sceneT = 0
    End If

    ' Draw current scene
    Select Case scenes(scene).id
    Case SCENE_STARFIELD : Effect_Starfield(dt)
    Case SCENE_PLASMA    : Effect_Plasma(sceneT)
    End Select

    DemoFlip()

    ' Frame-rate cap
    Dim elapsed As Double = Timer - tFrame
    If elapsed < 1.0 / DEMO_FPS Then Sleep CInt((1.0 / DEMO_FPS - elapsed) * 1000), 1
    tFrame = Timer

Loop Until MultiKey(SC_ESCAPE)

' ─── Shutdown ────────────────────────────────────────────────────────────────

DemoShutdown()
End
