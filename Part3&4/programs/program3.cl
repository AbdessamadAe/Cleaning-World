WORLD TurnBacktrackTest {
    SIZE(5, 5);
    ENTRY_DEF(2, 2, E);
    EXIT_DEF(4, 4, W);
}

AGENT NavigationAgent {
    MOVE;
    TURN LEFT;
    MOVE;
    TURN RIGHT;
    MOVE;
    BACKTRACK;
    REPORT 0;
}
