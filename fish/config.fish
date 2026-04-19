if status is-interactive
    set -g fish_greeting

    # Show fastfetch on shell launch (skip when explicitly disabled)
    if not set -q EINK_NO_FASTFETCH
        if not set -q __EINK_FASTFETCH_RAN
            set -g __EINK_FASTFETCH_RAN 1
            if type -q fastfetch
                fastfetch
            end
        end
    end
end
