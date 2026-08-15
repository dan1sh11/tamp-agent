(define (domain tamp-agent)

    (:requirements
        :strips
        :typing
    )

    (:types
        object
        receptacle
    )

    (:predicates

        ; Object is currently on the table.
        (on-table ?o - object)

        ; Robot is holding object.
        (holding ?o - object)

        ; Robot hand is empty.
        (hand-empty)

        ; Object is inside a receptacle.
        (in ?o - object ?r - receptacle)
    )

    ; --------------------------------------------------
    ; PICK
    ; --------------------------------------------------

    (:action pick
        :parameters (?o - object)

        :precondition
            (and
                (on-table ?o)
                (hand-empty)
            )

        :effect
            (and
                (holding ?o)
                (not (on-table ?o))
                (not (hand-empty))
            )
    )

    ; --------------------------------------------------
    ; PLACE
    ; --------------------------------------------------

    (:action place
        :parameters (
            ?o - object
            ?r - receptacle
        )

        :precondition
            (and
                (holding ?o)
            )

        :effect
            (and
                (in ?o ?r)
                (hand-empty)
                (not (holding ?o))
            )
    )
)