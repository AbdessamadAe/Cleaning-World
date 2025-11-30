WORLD ObstacleRelopTest {
    SIZE(8, 8);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(8, 8, S);
    OBSTACLE_DEF(4, 4);
    OBSTACLE_DEF(5, 5);
}

AGENT LogicAgent {
    VAR counter = 0;
    VAR limit = 10;
    VAR found = 0;
    
    WHILE counter LT limit DO
        IF SENSE OBSTACLE THEN
            found = 1;
        ELSE
            found = 0;
        ENDIF;
        
        IF found EQ 1 AND UNVISITED THEN
            BACKTRACK;
        ELSE
            IF counter NEQ 0 OR found EQ 1 THEN
                MOVE;
            ELSE
                MOVE;
            ENDIF;
        ENDIF;
        
        counter = counter + 1;
    ENDWHILE;
    
    IF limit GT counter THEN
        REPORT 0;
    ELSE
        REPORT 1;
    ENDIF;
}
