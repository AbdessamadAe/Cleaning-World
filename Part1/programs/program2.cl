WORLD SimpleWorld {
    SIZE(6, 6);
    ENTRY_DEF(1, 1, E);
    EXIT_DEF(6, 6, S);
    DIRT_DEF(2, 3);
}

FUNC add_one(x) RETURNS INT {
    RETURN x + 1;
}

AGENT CountCleaner {
    VAR dirt_collected = 0;

    WHILE UNVISITED DO
        MOVE;
        IF SENSE DIRT THEN
            CLEAN;
            dirt_collected = add_one(dirt_collected);
        ENDIF;
    ENDWHILE;

    REPORT dirt_collected;
}
