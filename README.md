This is a cipher image viewer.

The program never writes decrypted image to disk. So you needn't worry accidetal leak of you encrypted data if you turned your memory SWAP off.

`alias encode='python ~/projects/cipher_image_viewer/encrypt.py -e 3276437 -n 8598539'`
`alias encode_video='python ~/projects/cipher_image_viewer/encrypt.py -e 3276437 -n 8598539 --reverse'`

Put your decrypt key in $HOME/.config/cipher_image_viewer/decrypt_key, then you can decode.
`alias decode='python ~/projects/cipher_image_viewer/decrypt.py'`

View ciphered image.
`alias cv='python /home/sadtheslayer/projects/cipher_image_viewer/cipher_viewer.py'`

