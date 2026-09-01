#!/usr/bin/env bash

CONFIG_DIR="$HOME/.config/conky-study"
SIZE_FILE="$CONFIG_DIR/size"
CONKY_CONF="$CONFIG_DIR/conky.conf"
CARD_FILE="$CONFIG_DIR/card.png"

mkdir -p "$CONFIG_DIR"

if [ -f "$SIZE_FILE" ]; then
    CURRENT=$(cat "$SIZE_FILE")
else
    CURRENT="large"
fi

# Scale using ImageMagick if needed. Original card size is 760x470.
# Small card size is 500x310 (roughly 65%).
if [ ! -f "$CONFIG_DIR/card_large.png" ]; then
    cp "$CARD_FILE" "$CONFIG_DIR/card_large.png"
fi

if [ ! -f "$CONFIG_DIR/card_small.png" ]; then
    # try scaling using ImageMagick
    if command -v convert >/dev/null 2>&1; then
        convert "$CONFIG_DIR/card_large.png" -resize 500x310\! "$CONFIG_DIR/card_small.png"
    elif command -v magick >/dev/null 2>&1; then
        magick "$CONFIG_DIR/card_large.png" -resize 500x310\! "$CONFIG_DIR/card_small.png"
    else
        echo "ImageMagick not installed. Stretching existing card."
        cp "$CONFIG_DIR/card_large.png" "$CONFIG_DIR/card_small.png"
    fi
fi

if [ "$CURRENT" = "large" ]; then
    # Switch to small
    echo "small" > "$SIZE_FILE"
    echo "Switched to Small mode."
    
    # Update conky.conf
    sed -i 's/minimum_width = 760/minimum_width = 500/g' "$CONKY_CONF"
    sed -i 's/maximum_width = 760/maximum_width = 500/g' "$CONKY_CONF"
    sed -i 's/minimum_height = 470/minimum_height = 310/g' "$CONKY_CONF"
    sed -i 's/maximum_height = 470/maximum_height = 310/g' "$CONKY_CONF"
    sed -i 's/card.png -p 0,0 -s 760x470/card_small.png -p 0,0 -s 500x310/g' "$CONKY_CONF"
    sed -i 's/card_large.png -p 0,0 -s 760x470/card_small.png -p 0,0 -s 500x310/g' "$CONKY_CONF"

else
    # Switch to large
    echo "large" > "$SIZE_FILE"
    echo "Switched to Large mode."
    
    # Update conky.conf
    sed -i 's/minimum_width = 500/minimum_width = 760/g' "$CONKY_CONF"
    sed -i 's/maximum_width = 500/maximum_width = 760/g' "$CONKY_CONF"
    sed -i 's/minimum_height = 310/minimum_height = 470/g' "$CONKY_CONF"
    sed -i 's/maximum_height = 310/maximum_height = 470/g' "$CONKY_CONF"
    sed -i 's/card_small.png -p 0,0 -s 500x310/card_large.png -p 0,0 -s 760x470/g' "$CONKY_CONF"
    sed -i 's/card.png -p 0,0 -s 500x310/card_large.png -p 0,0 -s 760x470/g' "$CONKY_CONF"
fi

# Restart conky
pkill conky
nohup conky -c "$CONKY_CONF" >/tmp/conky-study.log 2>&1 &

echo "Dashboard resized and restarted!"
