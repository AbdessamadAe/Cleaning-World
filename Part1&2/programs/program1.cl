WORLD SmallRoom {
    SIZE(5, 5);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(5, 5, S);
    DIRT_DEF(3, 3);
}

AGENT BasicCleaner {
    VAR dirt_collected = 0;

    WHILE UNVISITED DO
        IF SENSE DIRT THEN
            CLEAN;
            dirt_collected = dirt_collected + 1;
        ELSE
            MOVE;
        ENDIF;
    ENDWHILE;

    REPORT dirt_collected;
}
