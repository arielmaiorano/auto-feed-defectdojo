###############################################################################
# Basado en:
# https://github.com/greenbone/gvm-tools/blob/master/scripts/scan-new-system.gmp.py
# https://github.com/greenbone/gvm-tools/blob/master/scripts/send-delta-emails.gmp.py
###############################################################################

import datetime
import time
import base64


def check_args(args):
    len_args = len(args.script) - 1
    message = """
        This script starts a new scan on the given host.
        * And waits for csv results report.

        1. <host_ip>     -- IP Address of the host system
        * 2. <filename>    -- Output CSV filename (results)

        Example:
        *    sudo -u nobody gvm-script --gmp-username XXX --gmp-password XXX tls [--hostname XXX.XXX.XXX.XXX] openvas_scan.py XXX.XXX.XXX.XXX XXX.csv
    """
    if len_args != 2:
        print(message)
        quit()


def create_target(gmp, ipaddress, port_list_id):
    # create a unique name by adding the current datetime
    name = "AFDD Scan Host {} {}".format(ipaddress, str(datetime.datetime.now()))

    response = gmp.create_target(
        name=name, hosts=[ipaddress], port_list_id=port_list_id
    )
    return response.get('id')


def create_task(gmp, ipaddress, target_id, scan_config_id, scanner_id):
    name = "AFDD Task Scan Host {}".format(ipaddress)
    response = gmp.create_task(
        name=name,
        config_id=scan_config_id,
        target_id=target_id,
        scanner_id=scanner_id,
    )
    return response.get('id')


def start_task(gmp, task_id):
    response = gmp.start_task(task_id)
    # the response is
    # <start_task_response><report_id>id</report_id></start_task_response>
    return response[0].text


def main(gmp, args):

    check_args(args)

    ipaddress = args.argv[1]
    output_filename = args.argv[2]

    port_list_id = '33d0cd82-57c6-11e1-8ed1-406186ea4fc5'

    target_id = create_target(gmp, ipaddress, port_list_id)

    full_and_fast_scan_config_id = 'daba56c8-73ec-11df-a475-002264764cea'
    openvas_scanner_id = '08b69003-5fc2-4037-a479-93b440211c73'
    task_id = create_task(
        gmp,
        ipaddress,
        target_id,
        full_and_fast_scan_config_id,
        openvas_scanner_id,
    )

    report_id = start_task(gmp, task_id)

    print(
        "Started scan of host {}. Corresponding report ID is {}".format(
            ipaddress, report_id
        )
    )

    tasks = gmp.get_tasks().xpath('task')
    print('Found %d task(s)' % (len(tasks), ))
    for task in tasks:

        tmp_task_id = task.xpath('@id')[0]
        print(
            'Processing task "%s" (%s)...'
            % (task.xpath('name/text()')[0], tmp_task_id)
        )

        if task_id != tmp_task_id:
            print('Not our task id...')
            continue

        while True:
            reports = gmp.get_reports(
                filter='task_id={0} and status=Done '
                'sort-reverse=date'.format(task_id)
            ).xpath('report')
            print('  Found %d report(s).' % len(reports))
            if len(reports) < 1:
                print('  Not finished, sleeping...')
                time.sleep(5)
            else:
                print('  Finished.')
                break

        report = gmp.get_report(
            report_id=reports[0].xpath('@id')[0],
            report_format_id='c1645568-627a-11e3-a660-406186ea4fc5',
        )

        csv_in_b64 = report.xpath('report/text()')[0]
        csv = base64.b64decode(csv_in_b64).decode('utf-8')

        print('  Writing report...')

        with open(output_filename, 'w') as out:
            out.write(csv)

        print('  Done.')

if __name__ == '__gmp__':
    # pylint: disable=undefined-variable
    main(gmp, args)
