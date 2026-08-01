using Godot;

namespace Aggga;

/// <summary>
/// A single game location. For now it owns only the click-to-walk loop:
/// clicking anywhere sends the character to the closest reachable point of
/// the room's navigation mesh. Hotspots and the verb-coin will plug in here,
/// consuming the click before the floor ever sees it.
/// </summary>
public partial class Room : Node2D
{
    // Assigned in the editor. Once several playable characters exist, the
    // room will ask the game state which one is active instead of holding a
    // direct reference — that is still an open decision in CLAUDE.md.
    [Export] private PlayerCharacter _player = null!;

    public override void _UnhandledInput(InputEvent @event)
    {
        // _UnhandledInput and not _Input: the UI (verb-coin, inventory) gets
        // to consume a click first, so pressing a button never also walks
        // the character to the floor underneath it.
        if (@event is not InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
            return;

        WalkToClickedPoint(GetGlobalMousePosition());
        GetViewport().SetInputAsHandled();
    }

    private void WalkToClickedPoint(Vector2 clickPosition)
    {
        // A navigation map is the server-side merge of every navigation
        // region in this world. Snapping the click to it means clicking a
        // wall walks to the floor in front of the wall instead of doing
        // nothing — the behaviour every adventure game of the era had.
        Rid navigationMap = GetWorld2D().NavigationMap;
        Vector2 target = NavigationServer2D.MapGetClosestPoint(navigationMap, clickPosition);

        _player.WalkTo(target);
    }
}
