# add multiple routes in parallel using multi processing

# Andrei Rad
import multiprocessing as mp
import subprocess


def add_routes(dest_ip, next_hop):
    subprocess.run(['ip', 'route', 'add', f'{dest_ip}/24', 'via', f'{next_hop}'])


if __name__ == '__main__':
    subprocess.run(['ip', 'addr', 'add', '192.168.100.100/24', 'dev', 'ens4'])
    processes = []
    for i in range(1, 5):
        p = mp.Process(target=add_routes, args=(f'192.168.10{i}.0', f'192.168.100.{1}'))
        processes.append(p)
    print("Starting to set routes")
    for proc in processes:
        proc.start()
    print("Setting routes")
    for proc in processes:
        proc.join()
    print("All processes finished")
