// starts from entry, unknown map

// moves by sensing

// incrementally builds & uses internal map

// cleans all reachable dirt

// backtracks out of tunnels

// exits via a valid exit (not the entry)

// reports total collected dirt


WORLD Maze10x10 {
    SIZE 10 10;
    ENTRY 1 1 N;
    EXIT 10 10 S;
    OBSTACLE_DEF (3,3), (3,4), (4,4);
    DIRT_DEF (2,2), (4,2), (8,5);
}

AGENT CleanAndExit {
    VAR dirtCount = 0;

    WHILE NOT (EXIT_FOUND AND NOT HAS_UNVISITED AND NOT SENSE DIRT) DO

        IF SENSE DIRT THEN
            CLEAN;
            dirtCount = dirtCount + 1;

        ELSE IF SENSE OBSTACLE THEN
            // Dead end or wall ahead: use map-based backtracking
            BACKTRACK;

        ELSE IF HAS_UNVISITED THEN
            // Use internal map to move toward some unvisited cell
            MOVE_TO_UNVISITED;

        ELSE
            // Safe unexplored or known free step ahead
            MOVE;
        ENDIF;

    ENDWHILE;

    REPORT dirtCount;
}
