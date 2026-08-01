using Godot;

namespace Aggga;

/// <summary>
/// Temporary root node of the technical prototype. For now it only confirms
/// that the C# build pipeline and the scene tree are wired up correctly.
/// The real game systems (rooms, hotspots, verb-coin, characters) will
/// replace this scene as development follows the plan in CLAUDE.md.
/// </summary>
public partial class Main : Node2D
{
    // In Godot 4 the C# node classes MUST be `partial`: the engine generates
    // extra code for them behind the scenes via a source generator.
    public override void _Ready()
    {
        // _Ready() runs once, after the node and its children enter the scene
        // tree. It's the Godot equivalent of a "startup" hook.
        GD.Print("AGGGA scaffold running — Godot + C# pipeline OK.");
    }
}
