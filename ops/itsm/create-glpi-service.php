<?php
require '/var/www/glpi/vendor/autoload.php';
use Glpi\Console\AbstractCommand;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Input\ArrayInput;
use Symfony\Component\Console\Output\ConsoleOutput;
$kernel = new Glpi\Kernel\Kernel();
$app = new Glpi\Console\Application($kernel);
$app->setAutoExit(false);
$app->add(new class('cosmotech:create-service') extends AbstractCommand {
 protected function execute(InputInterface $input, OutputInterface $output): int {
  $_SESSION["glpicronuserrunning"]="cosmotech-system-maintenance";
  $name='svc-cosmotech-automation';
  $user=new User();
  if ($user->getFromDBbyName($name)) { $output->writeln('Technical user already exists; refusing duplicate or password reset.'); return 2; }
  $entity=new Entity();
  if (!$entity->getFromDBByCrit(['name'=>'CosmoTech Lab Automation','entities_id'=>0])) {
   if (!$entity->add(['name'=>'CosmoTech Lab Automation','entities_id'=>0,'comment'=>'Isolated technical integration and functional test records'])) { throw new RuntimeException('Entity creation failed'); }
  }
  $entityId=$entity->getID();
  $profile=new Profile();
  if (!$profile->getFromDBByCrit(['name'=>'CosmoTech Automation Lab'])) {
   if (!$profile->add(['name'=>'CosmoTech Automation Lab','interface'=>'central','is_default'=>0,'ticket'=>READ|CREATE|UPDATE,'change'=>READ|CREATE|UPDATE,'followup'=>READ|CREATE,'document'=>READ|CREATE,'ticketvalidation'=>0,'changevalidation'=>0])) {throw new RuntimeException('Profile creation failed');}
  }
  Config::setConfigurationValues('core',['enable_hlapi'=>1]);
  $password=bin2hex(random_bytes(32));
  $uid=$user->add(['name'=>$name,'password'=>$password,'password2'=>$password,'is_active'=>1,'profiles_id'=>$profile->getID(),'entities_id'=>$entityId]);
  if (!$uid) {throw new RuntimeException('User creation failed');}
  $assignment=new Profile_User();
  if (!$assignment->getFromDBByCrit(['users_id'=>$uid,'profiles_id'=>$profile->getID(),'entities_id'=>$entityId])) {
   if (!$assignment->add(['users_id'=>$uid,'profiles_id'=>$profile->getID(),'entities_id'=>$entityId,'is_recursive'=>0,'is_dynamic'=>0])) {throw new RuntimeException('Profile assignment failed');}
  }
  foreach((new Profile_User())->find(['users_id'=>$uid,'entities_id'=>0]) as $row){(new Profile_User())->delete(['id'=>$row['id']]);}
  $client=new OAuthClient();
  if (!$client->getFromDBByCrit(['name'=>'CosmoTech Automation Lab'])) {
   $id=$client->add(['name'=>'CosmoTech Automation Lab','grants'=>['password','refresh_token'],'scopes'=>['api','user'],'allowed_ips'=>getenv('COSMOTECH_ALLOWED_IPS')]);
   if (!$id || !$client->getFromDB($id)) {throw new RuntimeException('OAuth client creation failed');}
  }
  $credentials=['username'=>$name,'password'=>$password,'client_id'=>$client->fields['identifier'],'client_secret'=>(new GLPIKey())->decrypt($client->fields['secret']),'entity_id'=>$entityId,'profile_id'=>$profile->getID(),'base_url'=>'http://127.0.0.1:8080'];
  file_put_contents('/tmp/cosmotech-glpi-service.json',json_encode($credentials));chmod('/tmp/cosmotech-glpi-service.json',0600);
  $output->writeln('Created technical user with isolated entity, restricted profile and OAuth password grant. No approval rights.');
  return 0;
 }
});
exit($app->run(new ArrayInput(['command'=>'cosmotech:create-service','--no-interaction'=>true]),new ConsoleOutput()));
