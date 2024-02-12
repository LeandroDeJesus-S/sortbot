import time
import random
import os
import logging

from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientConnectionError, ChallengeRequired, FeedbackRequired, PleaseWaitFewMinutes

BASEDIR = Path(__file__).parent.absolute()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

log.addHandler(console_handler)

def bot(username, pw, like_post, url_post, target_cmmt, n_mentions):
    USERNAME = username
    PASSWORD = pw

    session = Client()


    def make_login():
        session_file = os.path.join(BASEDIR, 'session.json')
        if os.path.exists(session_file):
            log.debug(f'LOGING WITH SAVED SESSION')
            saved_session = session.load_settings(session_file)
            session.set_settings(saved_session)
            login_result = session.login(USERNAME, PASSWORD)

            try:
                session.get_timeline_feed()
            except LoginRequired:
                log.debug(f'EXPIRED SESSION RELOGING')
                old_session = session.get_settings()

                session.set_settings({})
                session.set_uuids(old_session["uuids"])
                login_result = session.login(USERNAME, PASSWORD)
            

        else:
            log.debug('MAKING LOGIN')
            login_result = session.login(USERNAME, PASSWORD)
            session.dump_settings(session_file)
        
        return login_result


    login_result = make_login()
    log.info(f'LOGIN STATUS: {login_result}')

    post_pk = session.media_pk_from_url(url_post)
    post_info = session.media_info(post_pk).dict()

    comment_count = post_info['comment_count']
    log.info(f'Number of comments found: {comment_count}')

    target_comments = int(comment_count * float(target_cmmt))
    log.info(f'target of comments found: {target_comments}')

    def names_to_follow(filepath=os.path.join(BASEDIR, 'to_follow.txt')):
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            names = f.readlines()
            names = [name.replace('\n', '') for name in names]
        
        return names


    to_follow = names_to_follow()
    log.info(f'{len(to_follow)} people to follow')

    followers = session.user_followers(session.user_id)
    log.info(f'{len(followers)} followers found')

    following = session.user_following(session.user_id)
    log.info(f'following {len(following)} people')

    followers.update(following) # just for pratice to mentions

    if to_follow:
        try:
            for user in to_follow:
                uid = session.user_id_from_username(user)
                result = session.user_follow(uid)
                time.sleep(random.uniform(120, 240))
                log.info(f'user {user} followed.')

        except Exception as e:
            messagebox.showerror('Error', f'Erro ao seguir usuários: {e}')
            log.error(f'to_follow error: {e}')

    if like_post:
        result = session.media_like(post_pk)
        log.debug(f'like post status: {result}')


    def log_n_comments(n, fname):
        with open(fname, 'w+') as f:
            f.write(str(n))


    def restore_n_comments(fname):
        with open(fname, 'r') as f:
            n = f.read(1)
            n = int(n.replace('\n', '')) if n else 0
        
        return n


    chkpt_file = os.path.join(BASEDIR, '.checkpoint')
    comments = 0 if not os.path.exists(chkpt_file) else restore_n_comments(chkpt_file)

    while comments < target_comments:
        try:
            users_for_mention = list(followers.values())
            mentions = random.choices(users_for_mention, k=int(n_mentions))
            has_duplicates = list(map(lambda x: mentions.count(x) > 1, mentions))
            if True in has_duplicates:
                continue

            usernames = [f'@{u.username}' for u in mentions]
            text = ' '.join(usernames)

            session.media_comment(post_pk, text=text)
            log.debug(f'n_comments: {comments} - current commentary: {text}')
            time.sleep(random.uniform(120, 240))
            
            comments += 1
            log_n_comments(comments, chkpt_file)
        
        except KeyboardInterrupt:
            messagebox.showinfo('INFO', 'Execução interrompida pelo usuário.')
            log.error('comments interrupted by user')
            session.logout()
            break
        
        except FeedbackRequired:
            messagebox.showwarning('Warning', 'Você foi limitado de comentar.')
            break
        
        except Exception as e:
            if str(e) == 'failed to mention':
                log.warning(f'failed to mention {text}')
                continue

            log.error(f'comments error: {e}')
            break


    else:
        session.logout()
        os.remove(chkpt_file)
        log.warning(f'{chkpt_file} removed.')


def submit():
    user = entry_user.get()
    pw = entry_pw.get()
    url = entry_url.get()

    if not user or not pw or not url:
        messagebox.showinfo('Warning', 'Há campos não preenchidos.')
        return

    try:
        mention_number = int(entry_mentions.get())
        cmmt_target = int(entry_cmmt_tgt.get()) / 100
    except ValueError:
        messagebox.showinfo('Warning', 'Opção inválida! verifique os campos numéricos e tente novamente.')
        return
    
    like_post = True if checkbox_var.get() == 1 else False
    window.destroy()
    time.sleep(1)
    
    try:
        bot(**{
            'username': user,
            'pw': pw,
            'url_post': url,
            'like_post': like_post,
            'n_mentions': mention_number,
            'target_cmmt': cmmt_target,
        })

    except ClientConnectionError:
        messagebox.showwarning(
            'Warning', 
            'Erro de conexão! verifique sua internet e tente novamente.'
        )
        log.error('CONNECTION ERROR')

    except ChallengeRequired:
        messagebox.showwarning(
            'Warning', 
            'Capcha requirido. É recomendavel entrar manualmente \
            no instagram e esperar alguns minutos para a proxima execução.'
        )
        log.warn('Captcha requirido.')
    
    except PleaseWaitFewMinutes:
        messagebox.showwarning('Warning', 'Por favor, espere alguns minutos e tente novamente.')
    
    except FeedbackRequired:
        messagebox.showwarning('Warning', 'Você foi limitado de comentar.')
                
    except Exception as e:
        messagebox.showwarning('ERROR', f'Erro inesperado: {e}')
        log.error(f'Bot error: {e}')
    
    finally:
        time.sleep(3)  # for pyinstaller terminal before close


window = tk.Tk()
window.title("INSTABOT")

tk.Label(window, text="Usuário:").grid(row=0, column=0, sticky="e")
entry_user = tk.Entry(window)
entry_user.grid(row=0, column=1)

tk.Label(window, text="Senha:").grid(row=1, column=0, sticky="e")
entry_pw = tk.Entry(window, show="*")
entry_pw.grid(row=1, column=1)

tk.Label(window, text="URL do post:").grid(row=2, column=0, sticky="e")
entry_url = tk.Entry(window)
entry_url.grid(row=2, column=1)

tk.Label(window, text="Menções por comentário:").grid(row=3, column=0, sticky="e")
entry_mentions = tk.Entry(window)
entry_mentions.grid(row=3, column=1)

tk.Label(window, text="Meta de comentários %:").grid(row=4, column=0, sticky="e")
entry_cmmt_tgt = tk.Entry(window)
entry_cmmt_tgt.grid(row=4, column=1)

checkbox_var = tk.IntVar()
tk.Checkbutton(window, text="Curtir post", variable=checkbox_var).grid(row=5, columnspan=2)

tk.Button(window, text="Pronto", command=submit).grid(row=6, columnspan=2)

window.mainloop()
