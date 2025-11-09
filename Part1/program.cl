WORLD CleaningRoom {
    SIZE(10, 10);
    ENTRY(1, 1, N);
    EXIT(10, 10, S);
    OBSTACLE_DEF(3, 5);
    OBSTACLE_DEF(4, 5);
    DIRT_DEF(2, 3);
    DIRT_DEF(6, 7);
}


AGENT Explorer {
    VAR dirt_collected = 0;

    WHILE UNVISITED DO
        IF SENSE OBSTACLE THEN
            TURN RIGHT;
        ELSE
            MOVE;
            IF SENSE DIRT THEN
                CLEAN;
                dirt_collected = dirt_collected + 1;
            ENDIF;
        ENDIF;
    ENDWHILE;

    REPORT dirt_collected;
}
