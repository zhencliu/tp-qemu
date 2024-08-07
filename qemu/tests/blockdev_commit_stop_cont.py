from provider import backup_utils
from provider import job_utils

from provider.blockdev_commit_base import BlockDevCommitTest


class BlockdevCommitStopCont(BlockDevCommitTest):

    def commit_snapshots(self):
        device = self.params.get("device_tag")
        device_params = self.params.object_params(device)
        snapshot_tags = device_params["snapshot_tags"].split()
        self.device_node = self.get_node_name(device)
        options = ["base-node", "top-node", "speed"]
        arguments = self.params.copy_from_keys(options)
        arguments["base-node"] = self.get_node_name(device)
        arguments["top-node"] = self.get_node_name(snapshot_tags[-2])
        device = self.get_node_name(snapshot_tags[-1])
        commit_cmd = backup_utils.block_commit_qmp_cmd
        cmd, args = commit_cmd(device, **arguments)
        backup_utils.set_default_block_job_options(self.main_vm, args)
        self.main_vm.pause()
        self.main_vm.monitor.cmd(cmd, args)
        job_id = args.get("job-id", device)
        self.main_vm.resume()
        job_utils.wait_until_block_job_completed(self.main_vm, job_id)


def run(test, params, env):
    """
    Block commit base Test

    1. boot guest with system disk
    2. create 4 snapshots and save file in each snapshot
    3. stop vm
    4. commit snapshot 3 to base
    5. resume vm
    6. verify files's md5 after commit
    """

    block_test = BlockdevCommitStopCont(test, params, env)
    block_test.run_test()
