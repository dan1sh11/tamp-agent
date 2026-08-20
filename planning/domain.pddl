(define (domain tamp-agent)
    (:requirements :strips :typing)

    (:types
        object
        receptacle
    )

    (:predicates
        (on-table ?o - object)
        (holding ?o - object)
        (hand-empty)
        (in ?o - object ?r - receptacle)
    )

    (:action pick
        :parameters (?o - object)
        :precondition (and (on-table ?o) (hand-empty))
        :effect (and
            (holding ?o)
            (not (on-table ?o))
            (not (hand-empty))
        )
    )

    (:action drop
        :parameters (?o - object)
        :precondition (holding ?o)
        :effect (and
            (on-table ?o)
            (hand-empty)
            (not (holding ?o))
        )
    )

    (:action place
        :parameters (?o - object ?r - receptacle)
        :precondition (holding ?o)
        :effect (and
            (in ?o ?r)
            (hand-empty)
            (not (holding ?o))
        )
    )

    (:action move
        :parameters (?o - object ?r - receptacle)
        :precondition (and (on-table ?o) (hand-empty))
        :effect (and
            (in ?o ?r)
            (hand-empty)
            (not (on-table ?o))
        )
    )
)