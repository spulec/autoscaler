import boto
from mock import patch, call
from moto import mock_autoscaling
import sure  # noqa

from autoscaler.cli import _parse_drive_mapping, _parse_block_device_mappings


def test_ephemeral_drive():
	"""
	Ephemeral Drive
	"""
	user_input = "/dev/xvda=ephemeral0"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('ephemeral0')
	size.should.be.none
	delete.should.be.true
	iops.should.be.none


def test_snapshot_drive():
	"""
	Snapshot Drive
	"""
	user_input = "/dev/xvda=snap-1234abcd"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.be.none
	delete.should.be.true
	iops.should.be.none


def test_ebs_drive():
	"""
	EBS Drive
	"""
	user_input = "/dev/xvda=:100"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('')
	size.should.equal(100)
	delete.should.be.true
	iops.should.be.none


def test_drive_with_size():
	"""
	Drive with size
	"""
	user_input = "/dev/xvda=snap-1234abcd:100"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.equal(100)
	delete.should.be.true
	iops.should.be.none


def test_drive_with_no_size_no_delete_and_iops():
	"""
	Drive with iops
	"""
	user_input = "/dev/xvda=snap-1234abcd:::1000"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.be.none
	delete.should.be.true
	iops.should.equal(1000)


def test_drive_with_no_size_delete_and_no_iops():
	"""
	Drive with delete
	"""
	user_input = "/dev/xvda=snap-1234abcd::false:"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.be.none
	delete.should.be.false
	iops.should.be.none


def test_drive_with_size_and_delete():
	"""
	Drive with size and delete
	"""
	user_input = "/dev/xvda=snap-1234abcd:100:false"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.equal(100)
	delete.should.be.false
	iops.should.be.none


def test_drive_with_size_and_iops():
	"""
	Drive with size and iops
	"""
	user_input = "/dev/xvda=snap-1234abcd:100::1000"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.equal(100)
	delete.should.be.true
	iops.should.equal(1000)


def test_drive_with_delete_and_iops():
	"""
	Drive with delete and iops
	"""
	user_input = "/dev/xvda=snap-1234abcd::false:1000"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.be.none
	delete.should.be.false
	iops.should.equal(1000)


def test_drive_with_size_and_delete_and_iops():
	"""
	Drive with size, delete, and iops
	"""
	user_input = "/dev/xvda=snap-1234abcd:100:false:1000"
	mount_point, drive_type, size, delete, iops = _parse_drive_mapping(user_input)
	mount_point.should.equal('/dev/xvda')
	drive_type.should.equal('snap-1234abcd')
	size.should.equal(100)
	delete.should.be.false
	iops.should.equal(1000)


def test_single_ephemeral_input():
	"""
	Single Ephemeral Drive
	"""
	user_input = "/dev/xvda=ephemeral0"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.equal('ephemeral0')
	first_device.snapshot_id.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.be.none
	first_device.size.should.be.none
	first_device.delete_on_termination.should.be.true


def test_single_snapshot_input():
	"""
	Single Snapshot Drive
	"""
	user_input = "/dev/xvda=snap-1234abcd"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.be.none
	first_device.snapshot_id.should.equal('snap-1234abcd')
	first_device.iops.should.be.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.be.none
	first_device.delete_on_termination.should.be.true


def test_single_ebs_input():
	"""
	Single EBS Drive
	"""
	user_input = "/dev/xvda=:100"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.be.none
	first_device.snapshot_id.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.true


def test_single_with_iops():
	"""
	Single Drive with IOPS
	"""
	user_input = "/dev/xvda=:100::1000"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.be.none
	first_device.snapshot_id.should.be.none
	first_device.iops.should.equal(1000)
	first_device.volume_type.should.equal('io1')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.true


def test_single_with_delete():
	"""
	Single Drive without Delete on Termination
	"""
	user_input = "/dev/xvda=:100:false:"
	mapping = _parse_block_device_mappings(user_input)
	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.be.none
	first_device.snapshot_id.should.be.none
	first_device.iops.should.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.false


def test_multiple_ephemeral_input():
	"""
	Multiple Ephemeral Drives
	"""
	user_input = "/dev/xvda=ephemeral0,/dev/xvdb=ephemeral1"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.ephemeral_name.should.equal('ephemeral0')
	first_device.snapshot_id.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.be.none
	first_device.size.should.be.none
	first_device.delete_on_termination.should.be.true

	second_device = mapping['/dev/xvdb']
	second_device.ephemeral_name.should.equal('ephemeral1')
	second_device.snapshot_id.should.be.none
	second_device.iops.should.be.none
	second_device.volume_type.should.be.none
	second_device.size.should.be.none
	second_device.delete_on_termination.should.be.true


def test_multiple_snapshot_input():
	"""
	Multiple Snapshot Drives
	"""
	user_input = "/dev/xvda=snap-1234abcd,/dev/xvdb=snap-abcd1234"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.snapshot_id.should.equal('snap-1234abcd')
	first_device.ephemeral_name.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.be.none
	first_device.delete_on_termination.should.be.true

	second_device = mapping['/dev/xvdb']
	second_device.snapshot_id.should.equal('snap-abcd1234')
	second_device.ephemeral_name.should.be.none
	second_device.iops.should.be.none
	second_device.volume_type.should.equal('standard')
	second_device.size.should.be.none
	second_device.delete_on_termination.should.be.true


def test_multiple_ebs_input():
	"""
	Multiple EBS Drives
	"""
	user_input = "/dev/xvda=:100,/dev/xvdb=:200"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.snapshot_id.should.be.none
	first_device.ephemeral_name.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.true

	second_device = mapping['/dev/xvdb']
	second_device.snapshot_id.should.be.none
	second_device.ephemeral_name.should.be.none
	second_device.iops.should.be.none
	second_device.volume_type.should.equal('standard')
	second_device.size.should.equal(200)
	second_device.delete_on_termination.should.be.true


def test_multiple_with_iops():
	"""
	Multiple Drives with IOPS
	"""
	user_input = "/dev/xvda=:100::1000,/dev/xvdb=:200::2000"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.snapshot_id.should.be.none
	first_device.ephemeral_name.should.be.none
	first_device.iops.should.equal(1000)
	first_device.volume_type.should.equal('io1')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.true

	second_device = mapping['/dev/xvdb']
	second_device.snapshot_id.should.be.none
	second_device.ephemeral_name.should.be.none
	second_device.iops.should.equal(2000)
	second_device.volume_type.should.equal('io1')
	second_device.size.should.equal(200)
	second_device.delete_on_termination.should.be.true


def test_multiple_with_delete():
	"""
	Multiple Drives without Delete on Termination
	"""
	user_input = "/dev/xvda=:100:false:,/dev/xvdb=:200:false:"
	mapping = _parse_block_device_mappings(user_input)

	first_device = mapping['/dev/xvda']
	first_device.snapshot_id.should.be.none
	first_device.ephemeral_name.should.be.none
	first_device.iops.should.be.none
	first_device.volume_type.should.equal('standard')
	first_device.size.should.equal(100)
	first_device.delete_on_termination.should.be.false

	second_device = mapping['/dev/xvdb']
	second_device.snapshot_id.should.be.none
	second_device.ephemeral_name.should.be.none
	second_device.iops.should.be.none
	second_device.volume_type.should.equal('standard')
	second_device.size.should.equal(200)
	second_device.delete_on_termination.should.be.false
