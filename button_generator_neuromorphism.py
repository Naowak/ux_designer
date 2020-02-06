from PIL import Image, ImageDraw, ImageFont, ImageFilter


def rounded_rect(size, radius, color) :
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    size_x, size_y = size

    # Corner up left
    draw.pieslice(xy=[(0, 0), (2*radius, 2*radius)],
                  start=180,
                  end=270,
                  fill=color)
    # Corner up right
    draw.pieslice(xy=[(size_x-2*radius, 0), (size_x, 2*radius)],
                  start=270,
                  end=360,
                  fill=color)
    # Corner down left
    draw.pieslice(xy=[(0, size_y-2*radius), (2*radius, size_y)],
                  start=90,
                  end=180,
                  fill=color)
    # Corner down right
    draw.pieslice(xy=[(size_x-2*radius, size_y-2*radius), (size_x, size_y)],
                  start=0,
                  end=90,
                  fill=color)

    # Fill inside
    draw.rectangle(xy=[(0, radius), (radius, size_y-radius)],
                   fill=color)
    draw.rectangle(xy=[(radius, 0), (size_x-radius, size_y)],
                   fill=color)
    draw.rectangle(xy=[(size_x-radius, radius), (size_x, size_y-radius)],
                   fill=color)

    return img


def ux_area(size, corner_radius, color, coef_img=0.9, diff_light=30, diff_dark=30, gaussian_radius=5) :

    def fit_bg(img, bg, anchor, color) :
        color = tuple(list(color[:3]) + [0])
        new = Image.new('RGBA', bg.size, color)
        new.paste(img, anchor, img)
        return new

    def paste_image(img, bg, color) :
        # # Paste an image at the position anchor
        color = tuple(list(color[:3]) + [0])

        add_img = Image.new('RGBA', bg.size, (255, 255, 255, 0))
        add_img.paste(img, (0, 0), img)

        final = Image.new('RGBA', bg.size, (255, 255, 255, 0))
        final = Image.alpha_composite(final, bg)
        final = Image.alpha_composite(final, img)

        return final

    # compute colors
    color_light = tuple([c + diff_light for c in color[:3]] + [255])
    color_dark = tuple([c - diff_dark for c in color[:3]] + [255])

    # create imgs to paste
    size_rounded_rect = tuple((int(coef_img * s) for s in size))

    img_mid = rounded_rect(size_rounded_rect, corner_radius, color)
    img_light = rounded_rect(size_rounded_rect, corner_radius, color_light)
    img_dark = rounded_rect(size_rounded_rect, corner_radius, color_dark)

    # compute translation
    transfer = (1 - coef_img)/4
    translation = (int(transfer * size[0]), int(transfer * size[1]))

    # compute pos
    pos_light = translation
    pos_dark = (translation[0]*3, translation[1]*3)
    pos_mid = (translation[0]*2, translation[1]*2)

    # create background
    background = Image.new('RGBA', size, color)

    # fit imgs to background
    img_light = fit_bg(img_light, background, pos_light, color_light)
    img_dark = fit_bg(img_dark, background, pos_dark, color_dark)
    img_mid = fit_bg(img_mid, background, pos_mid, color)

    # apply gaussian filter
    img_light = img_light.filter(ImageFilter.GaussianBlur(radius=gaussian_radius))
    img_dark = img_dark.filter(ImageFilter.GaussianBlur(radius=gaussian_radius))

    # paste rounded rectangle
    background = paste_image(img_light, background, color_light)
    background = paste_image(img_dark, background, color_dark)
    background = paste_image(img_mid, background, color)
    background.show()

    return background





if __name__ == '__main__' :
    img = ux_area(size=(200, 70), corner_radius=20, color=(28, 28, 80, 255))
    img.save('test.png')