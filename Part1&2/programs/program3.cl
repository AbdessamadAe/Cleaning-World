WORLD MazeRoom {
    SIZE(8, 8);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(8, 8, E);
    OBSTACLE_DEF(4, 4);
    DIRT_DEF(3, 5);
}

AGENT Explorer {
    VAR cleaned = 0;

    WHILE UNVISITED DO
        IF (SENSE OBSTACLE) OR (NOT SENSE DIRT) THEN
            TURN RIGHT;
        ELSE
            MOVE;
            CLEAN;
            cleaned = cleaned + 1;
        ENDIF;

        IF NOT UNVISITED THEN
            BACKTRACK;
        ENDIF;
    ENDWHILE;

    REPORT cleaned;
}
